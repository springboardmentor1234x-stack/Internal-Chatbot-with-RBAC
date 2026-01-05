import sqlite3
from typing import Optional, Dict, List
from contextlib import contextmanager
from pathlib import Path
from config import Config

from .auth_handler import AuthHandler

class DatabaseManager:
    """SQLite database manager for user storage"""

    DB_PATH = Path(Config.DATABASE_URL.replace("sqlite:///", ""))

    def __init__(self):
        self.auth_handler = AuthHandler()
        # Create database directory if it doesn't exist
        self.DB_PATH.parent.mkdir(exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    def initialize_database(self):
        """Create users table if it doesn't exist"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index on username for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_username 
                ON users(username)
            """)
            
            conn.commit()
            print("✅ Users table created/verified")
    
    def seed_users(self):
        """Create default users for testing"""
        default_users = Config.DEFALUT_USERS
        
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
        """Retrieve user by username"""
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
        """Retrieve user by ID"""
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
        """Get all users (excluding password hashes)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, role, is_active, created_at
                FROM users
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row["id"],
                    "username": row["username"],
                    "role": row["role"],
                    "is_active": bool(row["is_active"]),
                    "created_at": row["created_at"]
                }
                for row in rows
            ]
    
    def update_user_status(self, username: str, is_active: bool) -> bool:
        """Enable or disable user account"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users
                SET is_active = ?, updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
            """, (is_active, username))
            
            conn.commit()
            
            return cursor.rowcount > 0
    
    def create_user(self, username: str, password: str, role: str) -> bool:
        """Create new user"""
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
    
    def update_user_password(self, username: str, new_password: str) -> bool:
        """Update user password"""
        password_hash = self.auth_handler.hash_password(new_password)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users
                SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
            """, (password_hash, username))
            
            conn.commit()
            
            return cursor.rowcount > 0
    
    def update_user_role(self, username: str, new_role: str) -> bool:
        """Update user role"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users
                SET role = ?, updated_at = CURRENT_TIMESTAMP
                WHERE username = ?
            """, (new_role, username))
            
            conn.commit()
            
            return cursor.rowcount > 0
    
    def delete_user(self, username: str) -> bool:
        """Delete user (use with caution)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM users
                WHERE username = ?
            """, (username,))
            
            conn.commit()
            
            return cursor.rowcount > 0