import os
import sqlite3

# Path for optional SQLite persistence
DB_PATH = os.path.join(os.path.dirname(__file__), "project.db")

# MODIFICATION: Using your specific plain-text password
COMMON_HASH = "P1a2ss3word"

def verify_password(plain_password, stored_password):
    """
    Direct string comparison to allow 'P1a2ss3word'.
    This avoids the Bcrypt UnknownHashError.
    """
    return plain_password == stored_password

FAKE_USERS_DB = {
    "intern": {
        "username": "intern", 
        "role": "Intern", 
        "password_hash": COMMON_HASH
    },
    "finance": {
        "username": "finance", 
        "role": "Finance", 
        "password_hash": COMMON_HASH
    },
    "admin": {
        "username": "admin", 
        "role": "Admin", 
        "password_hash": COMMON_HASH
    },
    "vidya": {
        "username": "vidya",
        "role": "Marketing",
        "password_hash": COMMON_HASH
    }
}

def get_user_from_db(username: str):
    """Retrieves user data from Mock DB or SQLite."""
    if username in FAKE_USERS_DB:
        return FAKE_USERS_DB[username]

    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT username, role, password_hash FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            conn.close()
            if row:
                return dict(row)
        except sqlite3.Error:
            pass
    return None