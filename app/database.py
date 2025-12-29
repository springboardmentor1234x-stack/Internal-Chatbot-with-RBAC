import os
import sqlite3
from passlib.context import CryptContext

# --- Configuration ---
# Password hashing context
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database Pathing
# This ensures project.db is found inside the 'app' folder
DB_PATH = os.path.join(os.path.dirname(__file__), "project.db")

# --- Mock Database for Testing ---
# All users here use the password: password123
FAKE_USERS_DB = {
    "admin": {
        "username": "admin", 
        "role": "Admin", 
        "password_hash": "$2b$12$0kL3K8J0j0k7yF0c9c7k4.H2.D5.G3.Y6.Z8.A0.B3.C5.E6.F9.G4"
    },
    "finance_user": {
        "username": "finance_user", 
        "role": "Finance", 
        "password_hash": "$2b$12$0kL3K8J0j0k7yF0c9c7k4.H2.D5.G3.Y6.Z8.A0.B3.C5.E6.F9.G4"
    },
}

def get_user_from_db(username: str):
    """
    Finds a user by username. 
    Checks the Mock DB first, then falls back to SQLite.
    """
    # 1. Check Mock Data first
    if username in FAKE_USERS_DB:
        return FAKE_USERS_DB[username]

    # 2. Check SQLite Database
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
        except sqlite3.Error as e:
            print(f"Database error: {e}")
    
    return None

def verify_password(plain_password, hashed_password):
    """Utility to check if a password is correct"""
    return PWD_CONTEXT.verify(plain_password, hashed_password)