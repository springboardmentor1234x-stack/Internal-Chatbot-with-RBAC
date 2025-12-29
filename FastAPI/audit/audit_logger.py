import json
from datetime import datetime
from pathlib import Path
from typing import Optional


class AuditLogger:    
    LOG_DIR = Path("FastAPI/logs")
    AUTH_LOG_FILE = LOG_DIR / "auth_audit.log"
    ACCESS_LOG_FILE = LOG_DIR / "access_audit.log"
    
    def __init__(self):
        # Create logs directory if it doesn't exist
        self.LOG_DIR.mkdir(exist_ok=True)
        
        # Initialize log files if they don't exist
        self.AUTH_LOG_FILE.touch(exist_ok=True)
        self.ACCESS_LOG_FILE.touch(exist_ok=True)
    
    def _write_log(self, filepath: Path, log_entry: dict):
        with open(filepath, 'a') as f:
            log_line = json.dumps(log_entry)
            f.write(log_line + '\n')
    
    def log_auth_attempt(
        self,
        username: str,
        action: str,
        success: bool,
        reason: Optional[str] = None
    ):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "authentication",
            "username": username,
            "action": action,
            "success": success,
            "reason": reason
        }
        
        self._write_log(self.AUTH_LOG_FILE, log_entry)
        
        # Also print to console for visibility
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"[AUTH] {status} | User: {username} | Action: {action} | Reason: {reason}")
    
    def log_access_attempt(
        self,
        username: str,
        role: str,
        endpoint: str,
        permission: str,
        allowed: bool,
        reason: Optional[str] = None
    ):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "access_control",
            "username": username,
            "role": role,
            "endpoint": endpoint,
            "permission_checked": permission,
            "allowed": allowed,
            "reason": reason
        }
        
        self._write_log(self.ACCESS_LOG_FILE, log_entry)
        
        # Also print to console for visibility
        status = "✅ ALLOWED" if allowed else "❌ DENIED"
        print(
            f"[ACCESS] {status} | User: {username} | Role: {role} | "
            f"Endpoint: {endpoint} | Permission: {permission} | Reason: {reason}"
        )
    
    def get_recent_auth_logs(self, limit: int = 50) -> list:
        try:
            with open(self.AUTH_LOG_FILE, 'r') as f:
                lines = f.readlines()
                
            # Get last N lines and parse JSON
            recent_logs = []
            for line in lines[-limit:]:
                try:
                    recent_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
            
            # Reverse to get most recent first
            return list(reversed(recent_logs))
        except FileNotFoundError:
            return []
    
    def get_recent_access_logs(self, limit: int = 50) -> list:
        try:
            with open(self.ACCESS_LOG_FILE, 'r') as f:
                lines = f.readlines()
                
            # Get last N lines and parse JSON
            recent_logs = []
            for line in lines[-limit:]:
                try:
                    recent_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
            
            # Reverse to get most recent first
            return list(reversed(recent_logs))
        except FileNotFoundError:
            return []
    
    def get_user_activity(self, username: str, limit: int = 20) -> dict:
        # Get all recent logs
        auth_logs = self.get_recent_auth_logs(limit=100)
        access_logs = self.get_recent_access_logs(limit=100)
        
        # Filter for specific user
        user_auth = [log for log in auth_logs if log.get("username") == username][:limit]
        user_access = [log for log in access_logs if log.get("username") == username][:limit]
        
        return {
            "username": username,
            "authentication_logs": user_auth,
            "access_logs": user_access
        }