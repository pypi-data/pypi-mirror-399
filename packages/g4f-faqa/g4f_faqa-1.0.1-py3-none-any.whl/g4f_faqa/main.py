# -*- coding: utf-8 -*-
"""
UseSupportLang(Fin)
---[]
// CREDIT: M1778 -> https://github.com/M1778
#[use(python_embed)]
export fun main() <noret> {
    pyfunc py_main <pyfunc.FuncType<PyObject>> = new pyfunc.newFunc("main");
    pylink.link(py_main);
    pyrun.set_run_mode(pyrun.RunExtention.EXTERNAL);
}
"""

import asyncio
import sqlite3
import pandas as pd
import os
import sys
import argparse
import subprocess
import logging
import base64
import traceback
from datetime import datetime
from typing import Optional
from tqdm.asyncio import tqdm
from dotenv import load_dotenv

# G4F
import g4f
from g4f.client import AsyncClient

# ==========================================
# تنظیمات لاگ و نمایش
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler("execution.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("LOG_M1778")

load_dotenv()

# SSSSSSSSS
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# لیست اولویت مدل‌ها
DEFAULT_MODEL_PRIORITY = [
    "gpt-4o",
    "gpt-4",
    "blackboxai", 
    "llama-3.3-70b",
    "gemini-1.5-flash",
    "claude-3.5-sonnet",
    "gpt-4o-mini",
]

class AIConfig:
    def __init__(self):
        # تنظیمات منوی راهنما 
        parser = argparse.ArgumentParser(
            description="سامانه هوشمند دریافت پاسخ از هوش مصنوعی ",
            formatter_class=argparse.RawTextHelpFormatter
        )
        
        # فایل‌ها
        parser.add_argument("--excel", default="questions.xlsx", help=" مسیر فایل اکسل ورودی (پیش‌فرض: questions.xlsx)")
        parser.add_argument("--db", default="QA.db", help=" مسیر دیتابیس جهت ذخیره‌سازی (پیش‌فرض: QA.db)")
        
        # تنظیمات سرعت
        parser.add_argument("--concurrency", type=int, default=4, help="تعداد درخواست‌های همزمان (پیش‌فرض: ۴)\n(اعداد بالاتر سرعت را زیاد می‌کنند اما ریسک مسدود شدن دارند)")
        parser.add_argument("--delay", type=float, default=1.0, help="تاخیر بین هر درخواست به ثانیه (جهت جلوگیری از بلاک شدن)")
        
        # تنظیمات دستی (طبق درخواست مشتری)
        parser.add_argument("--model", default=None, help="اجبار به استفاده از یک مدل خاص")
        parser.add_argument("--provider", default=None, help="اجبار به استفاده از یک سرویس‌دهنده خاص")
        
        # نگهداری
        parser.add_argument("--update", action="store_true", help="بروزرسانی هسته هوش مصنوعی به آخرین نسخه")
        
        self.args = parser.parse_args()
        
        if self.args.update:
            self.update_g4f()

    def update_g4f(self):
        print("Installing latest version of g4f...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", "g4f[all]"])
            print("بروزرسانی با موفقیت انجام شد. لطفاً برنامه را مجدداً اجرا کنید.")
            sys.exit(0)
        except Exception as e:
            print(f"خطا در بروزرسانی: {e}")
            sys.exit(1)

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS QA (id INTEGER PRIMARY KEY, question TEXT UNIQUE, answer TEXT)")

    def get_answer(self, question: str) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            res = conn.execute("SELECT answer FROM QA WHERE question=?", (question,)).fetchone()
            return res[0] if res else None

    def save_answer(self, question: str, answer: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO QA (question, answer) VALUES (?, ?)", (question, answer))
fetch_ = lambda : logger.info(base64.b64decode("VXNpbmcgbGFuZyBzdXBwb3J0IGZvciBNMTc3OA==").decode())
class SmartEngine:
    def __init__(self, config: AIConfig):
        self.config = config
        self.client = AsyncClient()
        self.semaphore = asyncio.Semaphore(config.args.concurrency)
        
        self.forced_provider = None
        if config.args.provider:
            if hasattr(g4f.Provider, config.args.provider):
                self.forced_provider = getattr(g4f.Provider, config.args.provider)
                print(f"حالت دستی فعال شد: استفاده اجباری از سرویس‌دهنده [{config.args.provider}]")
            else:
                print(f"سرویس‌دهنده '{config.args.provider}' یافت نشد! سیستم به حالت انتخاب خودکار بازگشت.")

    def is_truncated(self, text: str) -> bool:
        if not text: return False
        bad_endings = (':', ',', '(', '[', '{', '-', 'در', 'و', 'که', 'به')
        if text.strip()[-1] in bad_endings: return True
        if text.strip()[-1] not in ('.', '!', '?', '»', '"', '}') and len(text) > 400: return True
        return False

    async def ask_ai(self, question: str) -> Optional[str]:
        messages = [{"role": "user", "content": question}]
        
        models_to_try = [self.config.args.model] if self.config.args.model else DEFAULT_MODEL_PRIORITY
        
        async with self.semaphore:
            for model in models_to_try:
                try:
                    full_response = ""
                    
                    # تلاش مجدد برای هر مدل (۲ بار)
                    for _ in range(2): 
                        try:
                            response = await asyncio.wait_for(
                                self.client.chat.completions.create(
                                    model=model,
                                    messages=messages,
                                    provider=self.forced_provider
                                ), 
                                timeout=60
                            )
                            
                            content = response.choices[0].message.content
                            if not content: raise Exception("پاسخ خالی بود")
                            full_response += content

                            # 2. منطق ادامه دادن متن‌های طولانی (Auto-Continue)
                            if self.is_truncated(content):
                                messages.append({"role": "assistant", "content": content})
                                # دستور انگلیسی برای فهم بهتر هوش مصنوعی
                                messages.append({"role": "user", "content": "Please continue exactly from where you left off. (REMEMBER TO USE PERSIAN AS YOUR DEFAULT LANGUAGE)"})
                                await asyncio.sleep(1)
                                
                                # درخواست بخش دوم
                                response_cont = await asyncio.wait_for(
                                    self.client.chat.completions.create(
                                        model=model,
                                        messages=messages,
                                        provider=self.forced_provider
                                    ), timeout=60
                                )
                                full_response += response_cont.choices[0].message.content

                            # اگر موفق بود همینجا برگرد
                            return full_response.strip()

                        except Exception:
                            continue
                    
                except Exception as e:
                    continue
            
            return None

async def process_batch(config: AIConfig, db: DatabaseManager):
    engine = SmartEngine(config)
    
    try:
        df = pd.read_excel(config.args.excel)
        df['پاسخ'] = df['پاسخ'].astype(object)
    except Exception as e:
        print(f"خطای بحرانی: فایل اکسل باز نشد. \n{e}")
        return None

    # حذف ردیف‌های خالی
    df_valid = df[df['سوال'].notna() & (df['سوال'].str.strip() != '')]
    
    todo = []
    for idx, row in df_valid.iterrows():
        q = row['سوال']
        if not db.get_answer(q):
            todo.append((idx, q))
        else:
            df.at[idx, 'پاسخ'] = db.get_answer(q)

    print(f"تعداد کل سوالات: {len(df_valid)}")
    print(f"سوالات باقی‌مانده: {len(todo)}")
    print(f"حالت اجرا: {'دستی (Manual)' if config.args.model else 'خلبان خودکار (M1778::AutoPilot)'}")
    print(f"سرعت پردازش (همزمانی): {config.args.concurrency}")

    if not todo:
        print("تبریک! تمام سوالات قبلاً پاسخ داده شده‌اند.")
        return df

    async def worker(idx, q):
        ans = await engine.ask_ai(q)
        if ans:
            db.save_answer(q, ans)
            df.at[idx, 'پاسخ'] = ans
        else:
            pass
        
        await asyncio.sleep(config.args.delay)

    await tqdm.gather(*(worker(idx, q) for idx, q in todo), desc="پیشرفت پروژه")
    return df

def main():
    fetch_()
    start_time = datetime.now()
    print(f"زمان شروع: {start_time.strftime('%H:%M:%S')}")
    
    config = AIConfig()
    db = DatabaseManager(config.args.db)

    try:
        final_df = asyncio.run(process_batch(config, db))
        
        if final_df is not None:
            print("در حال ذخیره نهایی در فایل اکسل...")
            final_df.to_excel(config.args.excel, index=False)
            print("عملیات با موفقیت به پایان رسید.")
            
    except KeyboardInterrupt:
        print("\nعملیات توسط کاربر متوقف شد.")
    except Exception as e:
        traceback.print_exc()
        
    duration = datetime.now() - start_time
    print(f"مدت زمان کل اجرا: {duration}")

if __name__ == "__main__":
    main()

