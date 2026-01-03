
This program is used to process a batch of questions and generate answers based on AI models.
The questions are fetched from an Excel file and the answers are stored in a SQLite database.
The program uses asyncio to run the AI model and the SQLite database operations concurrently.
The program also uses tqdm to display a progress bar.
The AI model is configured using the AIConfig class.
The SQLite database is configured using the DatabaseManager class.
