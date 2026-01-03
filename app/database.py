import os
import sqlite3
from passlib.context import CryptContext
from typing import Optional, Dict

# --- Configuration ---
# Password hashing context
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database Pathing
DB_PATH = os.path.join(os.path.dirname(__file__), "project.db")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return PWD_CONTEXT.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def init_database():
    """Initialize the database with proper schema."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create users table with proper schema
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            role TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create default users if they don't exist
    default_users = [
        ("admin", "Admin", "password123"),
        ("finance_user", "Finance", "password123"),
        ("marketing_user", "Marketing", "password123"),
        ("hr_user", "HR", "password123"),
        ("engineering_user", "Engineering", "password123"),
        ("clevel_user", "C-Level", "password123"),
        ("employee_user", "Employee", "password123"),
        ("intern_user", "Intern", "password123"),
    ]

    for username, role, password in default_users:
        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            password_hash = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, role, password_hash) VALUES (?, ?, ?)",
                (username, role, password_hash),
            )

    conn.commit()
    conn.close()


def get_user_from_db(username: str) -> Optional[Dict]:
    """
    Finds a user by username from the database.
    Returns user dict or None if not found.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT username, role, password_hash FROM users WHERE username = ?",
            (username,),
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                "username": result[0],
                "role": result[1],
                "password_hash": result[2],
            }
        return None
    except Exception as e:
        print(f"Database error: {e}")
        return None


def authenticate_user(username: str, password: str) -> Optional[Dict]:
    """
    Authenticate a user with username and password.
    Returns user dict if valid, None otherwise.
    """
    user = get_user_from_db(username)
    if not user:
        return None

    if verify_password(password, user["password_hash"]):
        return user
    return None
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

            cursor.execute(
                "SELECT username, role, password_hash FROM users WHERE username = ?",
                (username,),
            )
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
