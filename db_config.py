import sqlite3
from sqlite3 import Error

# The path to your database file
DB_FILE = "project.db"

def get_connection():
    """Create and return a database connection."""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE)
        # This allows accessing columns by name: row['user_input']
        conn.row_factory = sqlite3.Row 
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
    return conn

def save_message(user_text, bot_text):
    """Helper function to log chat history."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (user_input, bot_response) VALUES (?, ?)",
            (user_text, bot_text)
        )
        conn.commit()
        conn.close()
        