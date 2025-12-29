import sqlite3
from typing import Optional, Dict, List
from contextlib import contextmanager

from auth.auth_handler import AuthHandler


class DatabaseManager:    
    DB_PATH = "FastAPI/database/users.db"
    
    def __init__(self):
        self.auth_handler = AuthHandler()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def initialize_database(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            print("✅ Users table created/verified")
    
    def seed_users(self):
        default_users = [
            {
                "username": "intern_user",
                "password": "intern123",
                "role": "intern"
            },
            {
                "username": "finance_user",
                "password": "finance123",
                "role": "finance_employee"
            },
            {
                "username": "admin_user",
                "password": "admin123",
                "role": "admin"
            }
        ]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for user in default_users:
                # Check if user already exists
                cursor.execute(
                    "SELECT id FROM users WHERE username = ?",
                    (user["username"],)
                )
                
                if cursor.fetchone() is None:
                    # Hash password and insert user
                    password_hash = self.auth_handler.hash_password(user["password"])
                    
                    cursor.execute("""
                        INSERT INTO users (username, password_hash, role, is_active)
                        VALUES (?, ?, ?, 1)
                    """, (user["username"], password_hash, user["role"]))
                    
                    print(f"✅ Created user: {user['username']} (role: {user['role']})")
                else:
                    print(f"ℹ️  User already exists: {user['username']}")
            
            conn.commit()
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, password_hash, role, is_active
                FROM users
                WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "username": row["username"],
                    "password_hash": row["password_hash"],
                    "role": row["role"],
                    "is_active": bool(row["is_active"])
                }
            
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, password_hash, role, is_active
                FROM users
                WHERE id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "username": row["username"],
                    "password_hash": row["password_hash"],
                    "role": row["role"],
                    "is_active": bool(row["is_active"])
                }
            
            return None
    
    def get_all_users(self) -> List[Dict]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, role, is_active
                FROM users
            """)
            
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row["id"],
                    "username": row["username"],
                    "role": row["role"],
                    "is_active": bool(row["is_active"])
                }
                for row in rows
            ]
    
    def update_user_status(self, username: str, is_active: bool) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users
                SET is_active = ?
                WHERE username = ?
            """, (is_active, username))
            
            conn.commit()
            
            return cursor.rowcount > 0
    
    def create_user(self, username: str, password: str, role: str) -> bool:
        try:
            password_hash = self.auth_handler.hash_password(password)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO users (username, password_hash, role, is_active)
                    VALUES (?, ?, ?, 1)
                """, (username, password_hash, role))
                
                conn.commit()
                return True
                
        except sqlite3.IntegrityError:
            # Username already exists
            return False