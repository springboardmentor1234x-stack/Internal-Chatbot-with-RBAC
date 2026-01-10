"""
Enhanced Chat History Management System
Provides persistent storage, search, and analytics for chat history.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import sqlite3
from pathlib import Path


class ChatHistoryManager:
    """
    Advanced chat history management with persistent storage and analytics.
    """
    
    def __init__(self, db_path: str = "app/chat_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the chat history database."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    session_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    user_role TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    total_messages INTEGER DEFAULT 0,
                    avg_accuracy REAL DEFAULT 0.0,
                    session_metadata TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    message_index INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    sources TEXT,
                    citations TEXT,
                    accuracy_score REAL,
                    original_accuracy REAL,
                    validation_score REAL,
                    confidence_level TEXT,
                    quality_metrics TEXT,
                    improvement_suggestions TEXT,
                    query_optimization TEXT,
                    query_category TEXT,
                    chunks_analyzed INTEGER,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions (session_id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_session_messages 
                ON chat_messages (session_id, message_index)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_username_timestamp 
                ON chat_sessions (username, start_time)
            """)
    
    def save_session(self, session_id: str, username: str, user_role: str, 
                    messages: List[Dict[str, Any]], session_metadata: Dict[str, Any] = None):
        """Save a complete chat session to the database."""
        
        with sqlite3.connect(self.db_path) as conn:
            # Calculate session statistics
            assistant_messages = [msg for msg in messages if msg.get("role") == "assistant"]
            avg_accuracy = 0.0
            if assistant_messages:
                accuracies = [msg.get("accuracy_score", 0) for msg in assistant_messages if msg.get("accuracy_score")]
                avg_accuracy = sum(accuracies) / len(accuracies) if accuracies else 0.0
            
            # Save session info
            conn.execute("""
                INSERT OR REPLACE INTO chat_sessions 
                (session_id, username, user_role, start_time, end_time, total_messages, avg_accuracy, session_metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                username,
                user_role,
                messages[0].get("timestamp", datetime.now().isoformat()) if messages else datetime.now().isoformat(),
                datetime.now().isoformat(),
                len(messages),
                avg_accuracy,
                json.dumps(session_metadata or {})
            ))
            
            # Clear existing messages for this session
            conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
            
            # Save messages
            for i, message in enumerate(messages):
                conn.execute("""
                    INSERT INTO chat_messages 
                    (session_id, message_index, role, content, timestamp, sources, citations,
                     accuracy_score, original_accuracy, validation_score, confidence_level,
                     quality_metrics, improvement_suggestions, query_optimization, 
                     query_category, chunks_analyzed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    i,
                    message.get("role", ""),
                    message.get("content", ""),
                    message.get("timestamp", datetime.now().isoformat()),
                    json.dumps(message.get("sources", [])),
                    json.dumps(message.get("citations", [])),
                    message.get("accuracy_score"),
                    message.get("original_accuracy"),
                    message.get("validation_score"),
                    message.get("confidence_level"),
                    json.dumps(message.get("quality_metrics", {})),
                    json.dumps(message.get("improvement_suggestions", [])),
                    json.dumps(message.get("query_optimization", {})),
                    message.get("query_category"),
                    message.get("chunks_analyzed")
                ))
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load a complete chat session from the database."""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get session info
            session_row = conn.execute(
                "SELECT * FROM chat_sessions WHERE session_id = ?", 
                (session_id,)
            ).fetchone()
            
            if not session_row:
                return None
            
            # Get messages
            message_rows = conn.execute("""
                SELECT * FROM chat_messages 
                WHERE session_id = ? 
                ORDER BY message_index
            """, (session_id,)).fetchall()
            
            messages = []
            for row in message_rows:
                message = {
                    "role": row["role"],
                    "content": row["content"],
                    "timestamp": row["timestamp"],
                    "sources": json.loads(row["sources"] or "[]"),
                    "citations": json.loads(row["citations"] or "[]"),
                    "accuracy_score": row["accuracy_score"],
                    "original_accuracy": row["original_accuracy"],
                    "validation_score": row["validation_score"],
                    "confidence_level": row["confidence_level"],
                    "quality_metrics": json.loads(row["quality_metrics"] or "{}"),
                    "improvement_suggestions": json.loads(row["improvement_suggestions"] or "[]"),
                    "query_optimization": json.loads(row["query_optimization"] or "{}"),
                    "query_category": row["query_category"],
                    "chunks_analyzed": row["chunks_analyzed"]
                }
                messages.append(message)
            
            return {
                "session_id": session_row["session_id"],
                "username": session_row["username"],
                "user_role": session_row["user_role"],
                "start_time": session_row["start_time"],
                "end_time": session_row["end_time"],
                "total_messages": session_row["total_messages"],
                "avg_accuracy": session_row["avg_accuracy"],
                "session_metadata": json.loads(session_row["session_metadata"] or "{}"),
                "messages": messages
            }
    
    def get_user_sessions(self, username: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent chat sessions for a user."""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            rows = conn.execute("""
                SELECT session_id, username, user_role, start_time, end_time, 
                       total_messages, avg_accuracy
                FROM chat_sessions 
                WHERE username = ? 
                ORDER BY start_time DESC 
                LIMIT ?
            """, (username, limit)).fetchall()
            
            return [dict(row) for row in rows]
    
    def search_messages(self, username: str, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search through user's chat messages."""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            rows = conn.execute("""
                SELECT cm.*, cs.username, cs.user_role, cs.start_time
                FROM chat_messages cm
                JOIN chat_sessions cs ON cm.session_id = cs.session_id
                WHERE cs.username = ? AND cm.content LIKE ?
                ORDER BY cm.timestamp DESC
                LIMIT ?
            """, (username, f"%{query}%", limit)).fetchall()
            
            results = []
            for row in rows:
                result = dict(row)
                result["sources"] = json.loads(result["sources"] or "[]")
                result["citations"] = json.loads(result["citations"] or "[]")
                result["quality_metrics"] = json.loads(result["quality_metrics"] or "{}")
                result["improvement_suggestions"] = json.loads(result["improvement_suggestions"] or "[]")
                result["query_optimization"] = json.loads(result["query_optimization"] or "{}")
                results.append(result)
            
            return results
    
    def get_user_analytics(self, username: str, days: int = 30) -> Dict[str, Any]:
        """Get analytics for a user's chat history."""
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Session statistics
            session_stats = conn.execute("""
                SELECT COUNT(*) as total_sessions,
                       AVG(total_messages) as avg_messages_per_session,
                       AVG(avg_accuracy) as overall_avg_accuracy,
                       MAX(avg_accuracy) as best_session_accuracy,
                       MIN(avg_accuracy) as worst_session_accuracy
                FROM chat_sessions 
                WHERE username = ? AND start_time >= ?
            """, (username, cutoff_date)).fetchone()
            
            # Message statistics
            message_stats = conn.execute("""
                SELECT COUNT(*) as total_messages,
                       COUNT(CASE WHEN role = 'user' THEN 1 END) as user_messages,
                       COUNT(CASE WHEN role = 'assistant' THEN 1 END) as assistant_messages,
                       AVG(accuracy_score) as avg_accuracy,
                       AVG(validation_score) as avg_validation_score
                FROM chat_messages cm
                JOIN chat_sessions cs ON cm.session_id = cs.session_id
                WHERE cs.username = ? AND cm.timestamp >= ?
            """, (username, cutoff_date)).fetchone()
            
            # Category breakdown
            category_stats = conn.execute("""
                SELECT query_category, 
                       COUNT(*) as count,
                       AVG(accuracy_score) as avg_accuracy
                FROM chat_messages cm
                JOIN chat_sessions cs ON cm.session_id = cs.session_id
                WHERE cs.username = ? AND cm.timestamp >= ? AND query_category IS NOT NULL
                GROUP BY query_category
                ORDER BY count DESC
            """, (username, cutoff_date)).fetchall()
            
            # Confidence level distribution
            confidence_stats = conn.execute("""
                SELECT confidence_level,
                       COUNT(*) as count
                FROM chat_messages cm
                JOIN chat_sessions cs ON cm.session_id = cs.session_id
                WHERE cs.username = ? AND cm.timestamp >= ? AND confidence_level IS NOT NULL
                GROUP BY confidence_level
                ORDER BY count DESC
            """, (username, cutoff_date)).fetchall()
            
            return {
                "period_days": days,
                "session_stats": dict(session_stats) if session_stats else {},
                "message_stats": dict(message_stats) if message_stats else {},
                "category_breakdown": [dict(row) for row in category_stats],
                "confidence_distribution": [dict(row) for row in confidence_stats]
            }
    
    def export_user_history(self, username: str, format: str = "json") -> str:
        """Export user's complete chat history."""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get all sessions for user
            sessions = conn.execute("""
                SELECT * FROM chat_sessions 
                WHERE username = ? 
                ORDER BY start_time DESC
            """, (username,)).fetchall()
            
            export_data = {
                "username": username,
                "export_timestamp": datetime.now().isoformat(),
                "total_sessions": len(sessions),
                "sessions": []
            }
            
            for session in sessions:
                session_data = dict(session)
                session_data["session_metadata"] = json.loads(session_data["session_metadata"] or "{}")
                
                # Get messages for this session
                messages = conn.execute("""
                    SELECT * FROM chat_messages 
                    WHERE session_id = ? 
                    ORDER BY message_index
                """, (session["session_id"],)).fetchall()
                
                session_messages = []
                for msg in messages:
                    message_data = dict(msg)
                    message_data["sources"] = json.loads(message_data["sources"] or "[]")
                    message_data["citations"] = json.loads(message_data["citations"] or "[]")
                    message_data["quality_metrics"] = json.loads(message_data["quality_metrics"] or "{}")
                    message_data["improvement_suggestions"] = json.loads(message_data["improvement_suggestions"] or "[]")
                    message_data["query_optimization"] = json.loads(message_data["query_optimization"] or "{}")
                    session_messages.append(message_data)
                
                session_data["messages"] = session_messages
                export_data["sessions"].append(session_data)
            
            if format.lower() == "json":
                return json.dumps(export_data, indent=2)
            else:
                # Could add other formats like CSV, HTML, etc.
                return json.dumps(export_data, indent=2)
    
    def cleanup_old_sessions(self, days: int = 90):
        """Clean up old chat sessions."""
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Delete old messages first (foreign key constraint)
            conn.execute("""
                DELETE FROM chat_messages 
                WHERE session_id IN (
                    SELECT session_id FROM chat_sessions 
                    WHERE start_time < ?
                )
            """, (cutoff_date,))
            
            # Delete old sessions
            result = conn.execute("""
                DELETE FROM chat_sessions 
                WHERE start_time < ?
            """, (cutoff_date,))
            
            return result.rowcount


# Global instance
chat_history_manager = ChatHistoryManager()