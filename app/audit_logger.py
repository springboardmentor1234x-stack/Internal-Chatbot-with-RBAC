"""
Audit Logger for FinSolve System
Tracks document access and login activities without affecting chatbot functionality
"""
import sqlite3
import os
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
import json

# Database path for audit logs
AUDIT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "audit_logs.db")

@contextmanager
def get_audit_db_connection():
    """Context manager for audit database connections"""
    conn = None
    try:
        conn = sqlite3.connect(AUDIT_DB_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    except Exception as e:
        print(f"Audit database error: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def initialize_audit_database():
    """Initialize audit database with required tables"""
    try:
        with get_audit_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create login audit table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS login_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    user_role TEXT NOT NULL,
                    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    login_date DATE NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    session_id TEXT,
                    success BOOLEAN DEFAULT 1
                )
            """)
            
            # Create document access audit table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_access_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    user_role TEXT NOT NULL,
                    document_name TEXT NOT NULL,
                    access_type TEXT NOT NULL, -- 'query', 'view', 'download'
                    query_text TEXT,
                    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    access_date DATE NOT NULL,
                    ip_address TEXT,
                    session_id TEXT,
                    access_granted BOOLEAN DEFAULT 1,
                    response_accuracy REAL,
                    chunks_accessed INTEGER DEFAULT 0
                )
            """)
            
            # Create daily login summary table for quick stats
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_login_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE UNIQUE NOT NULL,
                    total_logins INTEGER DEFAULT 0,
                    unique_users INTEGER DEFAULT 0,
                    successful_logins INTEGER DEFAULT 0,
                    failed_logins INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_login_date ON login_audit(login_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_login_username ON login_audit(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_access_date ON document_access_audit(access_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_access_username ON document_access_audit(username)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_access_document ON document_access_audit(document_name)")
            
            conn.commit()
            print("Audit database initialized successfully")
            
    except Exception as e:
        print(f"Failed to initialize audit database: {e}")

def log_login_attempt(username: str, user_role: str, success: bool = True, 
                     ip_address: str = None, user_agent: str = None, 
                     session_id: str = None) -> bool:
    """
    Log login attempt to audit database
    
    Args:
        username: User's username
        user_role: User's role
        success: Whether login was successful
        ip_address: User's IP address (optional)
        user_agent: User's browser/client info (optional)
        session_id: Session identifier (optional)
    
    Returns:
        bool: True if logged successfully, False otherwise
    """
    try:
        current_date = date.today()
        
        with get_audit_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert login record
            cursor.execute("""
                INSERT INTO login_audit 
                (username, user_role, login_date, ip_address, user_agent, session_id, success)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, user_role, current_date, ip_address, user_agent, session_id, success))
            
            # Update daily summary
            cursor.execute("""
                INSERT OR REPLACE INTO daily_login_summary 
                (date, total_logins, unique_users, successful_logins, failed_logins, last_updated)
                VALUES (
                    ?,
                    COALESCE((SELECT total_logins FROM daily_login_summary WHERE date = ?), 0) + 1,
                    (SELECT COUNT(DISTINCT username) FROM login_audit WHERE login_date = ?),
                    COALESCE((SELECT successful_logins FROM daily_login_summary WHERE date = ?), 0) + ?,
                    COALESCE((SELECT failed_logins FROM daily_login_summary WHERE date = ?), 0) + ?,
                    CURRENT_TIMESTAMP
                )
            """, (current_date, current_date, current_date, current_date, 
                  1 if success else 0, current_date, 0 if success else 1))
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"Failed to log login attempt: {e}")
        return False

def log_document_access(username: str, user_role: str, document_name: str, 
                       access_type: str = "query", query_text: str = None,
                       access_granted: bool = True, response_accuracy: float = None,
                       chunks_accessed: int = 0, ip_address: str = None,
                       session_id: str = None) -> bool:
    """
    Log document access to audit database
    
    Args:
        username: User's username
        user_role: User's role
        document_name: Name of accessed document
        access_type: Type of access ('query', 'view', 'download')
        query_text: The query that triggered document access (optional)
        access_granted: Whether access was granted
        response_accuracy: Accuracy score of the response (optional)
        chunks_accessed: Number of document chunks accessed
        ip_address: User's IP address (optional)
        session_id: Session identifier (optional)
    
    Returns:
        bool: True if logged successfully, False otherwise
    """
    try:
        current_date = date.today()
        
        with get_audit_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO document_access_audit 
                (username, user_role, document_name, access_type, query_text, 
                 access_date, ip_address, session_id, access_granted, 
                 response_accuracy, chunks_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (username, user_role, document_name, access_type, query_text,
                  current_date, ip_address, session_id, access_granted,
                  response_accuracy, chunks_accessed))
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"Failed to log document access: {e}")
        return False

def get_login_statistics(days: int = 30) -> Dict[str, Any]:
    """
    Get login statistics for the specified number of days
    
    Args:
        days: Number of days to look back (default: 30)
    
    Returns:
        Dict containing login statistics
    """
    try:
        with get_audit_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get daily login counts
            cursor.execute("""
                SELECT date, total_logins, unique_users, successful_logins, failed_logins
                FROM daily_login_summary
                WHERE date >= date('now', '-{} days')
                ORDER BY date DESC
            """.format(days))
            
            daily_stats = [dict(row) for row in cursor.fetchall()]
            
            # Get total statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_attempts,
                    COUNT(DISTINCT username) as unique_users,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_logins,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_logins
                FROM login_audit
                WHERE login_date >= date('now', '-{} days')
            """.format(days))
            
            totals = dict(cursor.fetchone())
            
            # Get login times by hour
            cursor.execute("""
                SELECT 
                    strftime('%H', login_time) as hour,
                    COUNT(*) as login_count
                FROM login_audit
                WHERE login_date >= date('now', '-{} days') AND success = 1
                GROUP BY strftime('%H', login_time)
                ORDER BY hour
            """.format(days))
            
            hourly_stats = [dict(row) for row in cursor.fetchall()]
            
            # Get top users by login count
            cursor.execute("""
                SELECT 
                    username,
                    user_role,
                    COUNT(*) as login_count,
                    MAX(login_time) as last_login
                FROM login_audit
                WHERE login_date >= date('now', '-{} days') AND success = 1
                GROUP BY username, user_role
                ORDER BY login_count DESC
                LIMIT 10
            """.format(days))
            
            top_users = [dict(row) for row in cursor.fetchall()]
            
            return {
                "period_days": days,
                "daily_statistics": daily_stats,
                "total_statistics": totals,
                "hourly_distribution": hourly_stats,
                "top_users": top_users,
                "generated_at": datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"Failed to get login statistics: {e}")
        return {"error": str(e)}

def get_document_access_statistics(days: int = 30) -> Dict[str, Any]:
    """
    Get document access statistics for the specified number of days
    
    Args:
        days: Number of days to look back (default: 30)
    
    Returns:
        Dict containing document access statistics
    """
    try:
        with get_audit_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get most accessed documents
            cursor.execute("""
                SELECT 
                    document_name,
                    COUNT(*) as access_count,
                    COUNT(DISTINCT username) as unique_users,
                    AVG(response_accuracy) as avg_accuracy,
                    SUM(chunks_accessed) as total_chunks
                FROM document_access_audit
                WHERE access_date >= date('now', '-{} days') AND access_granted = 1
                GROUP BY document_name
                ORDER BY access_count DESC
            """.format(days))
            
            document_stats = [dict(row) for row in cursor.fetchall()]
            
            # Get access by user role
            cursor.execute("""
                SELECT 
                    user_role,
                    COUNT(*) as access_count,
                    COUNT(DISTINCT username) as unique_users,
                    COUNT(DISTINCT document_name) as documents_accessed
                FROM document_access_audit
                WHERE access_date >= date('now', '-{} days') AND access_granted = 1
                GROUP BY user_role
                ORDER BY access_count DESC
            """.format(days))
            
            role_stats = [dict(row) for row in cursor.fetchall()]
            
            # Get daily access patterns
            cursor.execute("""
                SELECT 
                    access_date,
                    COUNT(*) as total_accesses,
                    COUNT(DISTINCT username) as unique_users,
                    COUNT(DISTINCT document_name) as documents_accessed,
                    AVG(response_accuracy) as avg_accuracy
                FROM document_access_audit
                WHERE access_date >= date('now', '-{} days') AND access_granted = 1
                GROUP BY access_date
                ORDER BY access_date DESC
            """.format(days))
            
            daily_access = [dict(row) for row in cursor.fetchall()]
            
            # Get access denied statistics
            cursor.execute("""
                SELECT 
                    user_role,
                    document_name,
                    COUNT(*) as denied_count
                FROM document_access_audit
                WHERE access_date >= date('now', '-{} days') AND access_granted = 0
                GROUP BY user_role, document_name
                ORDER BY denied_count DESC
                LIMIT 10
            """.format(days))
            
            access_denied = [dict(row) for row in cursor.fetchall()]
            
            return {
                "period_days": days,
                "document_statistics": document_stats,
                "role_statistics": role_stats,
                "daily_access_patterns": daily_access,
                "access_denied_statistics": access_denied,
                "generated_at": datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"Failed to get document access statistics: {e}")
        return {"error": str(e)}

def get_audit_dashboard_data() -> Dict[str, Any]:
    """
    Get comprehensive audit data for dashboard display
    
    Returns:
        Dict containing all audit statistics
    """
    try:
        login_stats = get_login_statistics(30)
        doc_stats = get_document_access_statistics(30)
        
        # Get today's quick stats
        with get_audit_db_connection() as conn:
            cursor = conn.cursor()
            
            # Today's login count
            cursor.execute("""
                SELECT COUNT(*) as today_logins
                FROM login_audit
                WHERE login_date = date('now') AND success = 1
            """)
            today_logins = cursor.fetchone()[0]
            
            # Today's document accesses
            cursor.execute("""
                SELECT COUNT(*) as today_accesses
                FROM document_access_audit
                WHERE access_date = date('now') AND access_granted = 1
            """)
            today_accesses = cursor.fetchone()[0]
            
            # Active users today
            cursor.execute("""
                SELECT COUNT(DISTINCT username) as active_users
                FROM login_audit
                WHERE login_date = date('now') AND success = 1
            """)
            active_users = cursor.fetchone()[0]
        
        return {
            "today_summary": {
                "logins": today_logins,
                "document_accesses": today_accesses,
                "active_users": active_users
            },
            "login_analytics": login_stats,
            "document_analytics": doc_stats,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Failed to get audit dashboard data: {e}")
        return {"error": str(e)}

# Initialize audit database when module is imported
try:
    initialize_audit_database()
    print("Audit logger initialized successfully")
except Exception as e:
    print(f"Failed to initialize audit logger: {e}")