import os
import sqlite3
from passlib.context import CryptContext
from typing import Optional, Dict, Any
from contextlib import contextmanager

# Import error handling
try:
    from .error_handler import (
        DatabaseError, AuthenticationError, ValidationError,
        handle_exceptions, safe_execute, logger, ErrorSeverity
    )
except ImportError:
    from error_handler import (
        DatabaseError, AuthenticationError, ValidationError,
        handle_exceptions, safe_execute, logger, ErrorSeverity
    )

# --- Configuration ---
# Password hashing context
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Database Pathing
# This ensures project.db is found inside the 'app' folder
DB_PATH = os.path.join(os.path.dirname(__file__), "project.db")

@contextmanager
def get_db_connection():
    """
    Context manager for database connections with proper error handling
    """
    conn = None
    try:
        if not os.path.exists(DB_PATH):
            logger.warning(f"Database file does not exist at {DB_PATH}, will be created on first write")
        
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row
        
        # Enable foreign key constraints
        conn.execute("PRAGMA foreign_keys = ON")
        
        logger.debug(f"Database connection established: {DB_PATH}")
        yield conn
        
    except sqlite3.OperationalError as e:
        logger.error(f"Database operational error: {e}")
        raise DatabaseError(
            f"Database is locked or inaccessible: {str(e)}",
            details={"db_path": DB_PATH, "error_type": "operational"},
            suggestions=[
                "Check if another process is using the database",
                "Verify database file permissions",
                "Try again in a few moments"
            ]
        )
    except sqlite3.DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise DatabaseError(
            f"Database error occurred: {str(e)}",
            details={"db_path": DB_PATH, "error_type": "database"},
            suggestions=[
                "Check database file integrity",
                "Verify database schema",
                "Contact system administrator if problem persists"
            ]
        )
    except Exception as e:
        logger.error(f"Unexpected database error: {e}")
        raise DatabaseError(
            f"Unexpected database error: {str(e)}",
            details={"db_path": DB_PATH, "error_type": "unexpected"},
            suggestions=["Contact system administrator"]
        )
    finally:
        if conn:
            try:
                conn.close()
                logger.debug("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")


@handle_exceptions(return_dict=True)
def initialize_database():
    """
    Initialize database with proper schema and error handling
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create users table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'Employee',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    failed_login_attempts INTEGER DEFAULT 0,
                    locked_until TIMESTAMP NULL
                )
            """)
            
            # Create sessions table for session management
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    session_token TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    FOREIGN KEY (username) REFERENCES users (username)
                )
            """)
            
            # Create error_logs table for tracking errors
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_code TEXT NOT NULL,
                    category TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    user_id TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT,
                    resolved BOOLEAN DEFAULT 0
                )
            """)
            
            conn.commit()
            logger.info("Database initialized successfully")
            return {"success": True, "message": "Database initialized"}
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise DatabaseError(
            f"Failed to initialize database: {str(e)}",
            details={"operation": "initialize_database"},
            suggestions=[
                "Check database file permissions",
                "Verify disk space availability",
                "Contact system administrator"
            ]
        )


@handle_exceptions(return_dict=True)
def create_user(username: str, password: str, role: str = "Employee") -> Dict[str, Any]:
    """
    Create a new user with proper validation and error handling
    """
    # Validate inputs
    if not username or not username.strip():
        raise ValidationError(
            "Username cannot be empty",
            details={"field": "username"},
            suggestions=["Please provide a valid username"]
        )
    
    if not password or len(password) < 6:
        raise ValidationError(
            "Password must be at least 6 characters long",
            details={"field": "password", "min_length": 6},
            suggestions=["Please provide a password with at least 6 characters"]
        )
    
    valid_roles = ["Employee", "HR", "Finance", "Marketing", "Engineering", "C-Level"]
    if role not in valid_roles:
        raise ValidationError(
            f"Invalid role: {role}",
            details={"field": "role", "valid_roles": valid_roles},
            suggestions=[f"Please use one of: {', '.join(valid_roles)}"]
        )
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                raise ValidationError(
                    f"User '{username}' already exists",
                    details={"username": username},
                    suggestions=["Please choose a different username"]
                )
            
            # Hash password
            password_hash = PWD_CONTEXT.hash(password)
            
            # Insert new user
            cursor.execute("""
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, ?)
            """, (username, password_hash, role))
            
            conn.commit()
            user_id = cursor.lastrowid
            
            logger.info(f"User created successfully: {username} (ID: {user_id})")
            return {
                "success": True,
                "message": f"User '{username}' created successfully",
                "user_id": user_id
            }
            
    except ValidationError:
        raise  # Re-raise validation errors
    except sqlite3.IntegrityError as e:
        logger.error(f"Database integrity error creating user: {e}")
        raise DatabaseError(
            f"Failed to create user due to data conflict: {str(e)}",
            details={"username": username, "error_type": "integrity"},
            suggestions=["Username may already exist", "Try a different username"]
        )
    except Exception as e:
        logger.error(f"Unexpected error creating user: {e}")
        raise DatabaseError(
            f"Failed to create user: {str(e)}",
            details={"username": username, "operation": "create_user"},
            suggestions=["Contact system administrator"]
        )


# --- Mock Database for Testing ---
# All users here use the password: password123
FAKE_USERS_DB = {
    "admin": {
        "username": "admin",
        "role": "C-Level",
        "password_hash": PWD_CONTEXT.hash("password123"),
    },
    "finance_user": {
        "username": "finance_user",
        "role": "Finance",
        "password_hash": PWD_CONTEXT.hash("password123"),
    },
    "marketing_user": {
        "username": "marketing_user",
        "role": "Marketing",
        "password_hash": PWD_CONTEXT.hash("password123"),
    },
    "hr_user": {
        "username": "hr_user",
        "role": "HR",
        "password_hash": PWD_CONTEXT.hash("password123"),
    },
    "engineering_user": {
        "username": "engineering_user",
        "role": "Engineering",
        "password_hash": PWD_CONTEXT.hash("password123"),
    },
    "employee": {
        "username": "employee",
        "role": "Employee",
        "password_hash": PWD_CONTEXT.hash("password123"),
    },
}


@handle_exceptions(return_dict=True)
def get_user_from_db(username: str) -> Optional[Dict[str, Any]]:
    """
    Finds a user by username with comprehensive error handling.
    Checks the Mock DB first, then falls back to SQLite.
    """
    if not username or not username.strip():
        raise ValidationError(
            "Username cannot be empty",
            details={"field": "username"},
            suggestions=["Please provide a valid username"]
        )
    
    username = username.strip()
    
    try:
        # 1. Check Mock Data first
        if username in FAKE_USERS_DB:
            logger.debug(f"User found in mock database: {username}")
            return FAKE_USERS_DB[username]

        # 2. Check SQLite Database
        if os.path.exists(DB_PATH):
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()

                    cursor.execute("""
                        SELECT username, role, password_hash, is_active, 
                               failed_login_attempts, locked_until
                        FROM users 
                        WHERE username = ? AND is_active = 1
                    """, (username,))
                    
                    row = cursor.fetchone()
                    
                    if row:
                        user_data = dict(row)
                        logger.debug(f"User found in database: {username}")
                        
                        # Check if account is locked
                        if user_data.get('locked_until'):
                            from datetime import datetime
                            locked_until = datetime.fromisoformat(user_data['locked_until'])
                            if datetime.now() < locked_until:
                                raise AuthenticationError(
                                    f"Account is temporarily locked until {locked_until}",
                                    details={"username": username, "locked_until": str(locked_until)},
                                    suggestions=["Wait for the lock period to expire", "Contact administrator"]
                                )
                        
                        return user_data
                    else:
                        logger.debug(f"User not found in database: {username}")
                        return None
                        
            except DatabaseError:
                raise  # Re-raise database errors
            except Exception as e:
                logger.error(f"Error querying user database: {e}")
                raise DatabaseError(
                    f"Failed to query user database: {str(e)}",
                    details={"username": username, "operation": "get_user"},
                    suggestions=["Check database connectivity", "Try again later"]
                )
        else:
            logger.warning(f"Database file does not exist: {DB_PATH}")
            return None

    except ValidationError:
        raise  # Re-raise validation errors
    except (AuthenticationError, DatabaseError):
        raise  # Re-raise our custom errors
    except Exception as e:
        logger.error(f"Unexpected error in get_user_from_db: {e}")
        raise DatabaseError(
            f"Unexpected error retrieving user: {str(e)}",
            details={"username": username},
            suggestions=["Contact system administrator"]
        )


@handle_exceptions(return_dict=True)
def update_login_attempt(username: str, success: bool = True) -> Dict[str, Any]:
    """
    Update user login attempt information with error handling
    """
    if not username:
        raise ValidationError("Username cannot be empty")
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if success:
                # Reset failed attempts and update last login
                cursor.execute("""
                    UPDATE users 
                    SET failed_login_attempts = 0, 
                        locked_until = NULL,
                        last_login = CURRENT_TIMESTAMP
                    WHERE username = ?
                """, (username,))
                logger.info(f"Successful login recorded for user: {username}")
            else:
                # Increment failed attempts
                cursor.execute("""
                    UPDATE users 
                    SET failed_login_attempts = failed_login_attempts + 1
                    WHERE username = ?
                """, (username,))
                
                # Check if account should be locked (after 5 failed attempts)
                cursor.execute("""
                    SELECT failed_login_attempts FROM users WHERE username = ?
                """, (username,))
                
                row = cursor.fetchone()
                if row and row['failed_login_attempts'] >= 5:
                    from datetime import datetime, timedelta
                    lock_until = datetime.now() + timedelta(minutes=30)
                    
                    cursor.execute("""
                        UPDATE users 
                        SET locked_until = ?
                        WHERE username = ?
                    """, (lock_until.isoformat(), username))
                    
                    logger.warning(f"Account locked due to failed attempts: {username}")
                
                logger.warning(f"Failed login attempt recorded for user: {username}")
            
            conn.commit()
            return {"success": True, "message": "Login attempt recorded"}
            
    except Exception as e:
        logger.error(f"Error updating login attempt: {e}")
        raise DatabaseError(
            f"Failed to update login attempt: {str(e)}",
            details={"username": username, "success": success},
            suggestions=["Contact system administrator"]
        )


@handle_exceptions(return_dict=True)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Utility to check if a password is correct with error handling
    """
    if not plain_password or not hashed_password:
        raise ValidationError(
            "Password and hash cannot be empty",
            details={"has_password": bool(plain_password), "has_hash": bool(hashed_password)},
            suggestions=["Provide both password and hash for verification"]
        )
    
    try:
        result = PWD_CONTEXT.verify(plain_password, hashed_password)
        logger.debug(f"Password verification result: {result}")
        return result
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        raise AuthenticationError(
            f"Password verification failed: {str(e)}",
            details={"error_type": "verification"},
            suggestions=["Check password format", "Try again"]
        )


@handle_exceptions(return_dict=True)
def log_error_to_db(error_code: str, category: str, severity: str, message: str, 
                   user_id: str = None, details: str = None) -> Dict[str, Any]:
    """
    Log error information to database for tracking and analysis
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO error_logs (error_code, category, severity, message, user_id, details)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (error_code, category, severity, message, user_id, details))
            
            conn.commit()
            log_id = cursor.lastrowid
            
            return {"success": True, "log_id": log_id}
            
    except Exception as e:
        # Don't raise errors for logging failures to avoid infinite loops
        logger.error(f"Failed to log error to database: {e}")
        return {"success": False, "error": str(e)}


@handle_exceptions(return_dict=True)
def get_error_statistics() -> Dict[str, Any]:
    """
    Get error statistics from database
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get error counts by category
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM error_logs
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY category
                ORDER BY count DESC
            """)
            category_stats = dict(cursor.fetchall())
            
            # Get error counts by severity
            cursor.execute("""
                SELECT severity, COUNT(*) as count
                FROM error_logs
                WHERE timestamp >= datetime('now', '-7 days')
                GROUP BY severity
                ORDER BY count DESC
            """)
            severity_stats = dict(cursor.fetchall())
            
            # Get recent errors
            cursor.execute("""
                SELECT error_code, category, severity, message, timestamp
                FROM error_logs
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            recent_errors = [dict(row) for row in cursor.fetchall()]
            
            return {
                "success": True,
                "statistics": {
                    "by_category": category_stats,
                    "by_severity": severity_stats,
                    "recent_errors": recent_errors
                }
            }
            
    except Exception as e:
        logger.error(f"Failed to get error statistics: {e}")
        return {"success": False, "error": str(e)}


# Initialize database on module import
try:
    init_result = initialize_database()
    if init_result.get("success"):
        logger.info("Database module initialized successfully")
    else:
        logger.error(f"Database initialization failed: {init_result}")
except Exception as e:
    logger.error(f"Failed to initialize database module: {e}")
