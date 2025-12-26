import os
import sqlite3

# This finds the folder where this file sits, then goes up one level to the root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(os.path.dirname(__file__), "project.db")

def get_user_from_db(username: str):
    # Now it will always find project.db in the internalchatbot folder
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # ... rest of your code