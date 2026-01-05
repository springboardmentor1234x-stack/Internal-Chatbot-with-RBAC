import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from config import Config

class AuditLogger:
    """Unified audit logging for both RAG pipeline and authentication/access control"""
    
    # File-based logging paths
    AUTH_LOG_FILE = Config.AUTH_LOG_FILE
    ACCESS_LOG_FILE = Config.ACCESS_LOG_FILE
    RAG_LOG_FILE = Config.RAG_LOG_FILE

    def __init__(self, log_level=logging.INFO, enable_console=True, enable_file=True):
        self.enable_console = enable_console
        self.enable_file = enable_file
        
        # Initialize log files
        if enable_file:
            self.AUTH_LOG_FILE.touch(exist_ok=True)
            self.ACCESS_LOG_FILE.touch(exist_ok=True)
            self.RAG_LOG_FILE.touch(exist_ok=True)
        
        # Setup console logger
        if enable_console:
            self.logger = logging.getLogger("UnifiedAudit")
            self.logger.setLevel(log_level)
            
            if not self.logger.handlers:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(log_level)
                formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
    
    # ==================== FILE-BASED LOGGING ====================
    
    def _write_log(self, filepath: Path, log_entry: dict):
        """Write log entry to file"""
        if not self.enable_file:
            return
        try:
            with open(filepath, 'a') as f:
                log_line = json.dumps(log_entry)
                f.write(log_line + '\n')
        except Exception as e:
            if self.enable_console:
                self.logger.error(f"Failed to write log: {e}")
    
    # ==================== AUTHENTICATION LOGGING ====================
    
    def log_auth_attempt(
        self,
        username: str,
        action: str,
        success: bool,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log authentication attempts"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "authentication",
            "username": username,
            "action": action,
            "success": success,
            "reason": reason,
            "ip_address": ip_address
        }
        
        self._write_log(self.AUTH_LOG_FILE, log_entry)
        
        if self.enable_console:
            status = "✅ SUCCESS" if success else "❌ FAILED"
            self.logger.info(
                f"[AUTH] {status} | User: {username} | Action: {action} | Reason: {reason}"
            )
    
    def log_access_attempt(
        self,
        username: str,
        role: str,
        endpoint: str,
        permission: str,
        allowed: bool,
        reason: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log access control attempts"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "access_control",
            "username": username,
            "role": role,
            "endpoint": endpoint,
            "permission_checked": permission,
            "allowed": allowed,
            "reason": reason,
            "ip_address": ip_address
        }
        
        self._write_log(self.ACCESS_LOG_FILE, log_entry)
        
        if self.enable_console:
            status = "✅ ALLOWED" if allowed else "❌ DENIED"
            self.logger.info(
                f"[ACCESS] {status} | User: {username} | Role: {role} | "
                f"Endpoint: {endpoint} | Permission: {permission}"
            )
    
    # ==================== RAG PIPELINE LOGGING ====================
    
    def log_query_start(self, query: str, user_roles: List[str], username: Optional[str] = None):
        """Log the start of RAG query processing"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "rag_query_start",
            "username": username,
            "query": query,
            "user_roles": user_roles
        }
        self._write_log(self.RAG_LOG_FILE, log_entry)
        
        if self.enable_console:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"RAG Query Processing Started")
            self.logger.info(f"User: {username} | Query: \"{query}\"")
            self.logger.info(f"User Roles: {user_roles}")
            self.logger.info(f"{'='*60}\n")
    
    def log_normalization(self, original: str, normalized: str):
        """Log query normalization"""
        if self.enable_console:
            self.logger.info("Step 1: Query Normalization")
            self.logger.info(f"  Original: {original}")
            self.logger.info(f"  Normalized: {normalized}\n")
    
    def log_query_variants(self, variants: List[str]):
        """Log generated query variants"""
        if self.enable_console:
            self.logger.info("Step 2: Query Expansion")
            self.logger.info(f"  Generated {len(variants)} query variants")
            for i, variant in enumerate(variants, 1):
                self.logger.info(f"    {i}. {variant}")
            self.logger.info("")
    
    def log_rbac_resolution(self, user_roles: List[str], effective_roles: set, 
                           permissions: set, accessible_depts: List[str]):
        """Log RBAC role resolution and permissions"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "rag_rbac_resolution",
            "user_roles": user_roles,
            "effective_roles": list(effective_roles),
            "permissions": list(permissions),
            "accessible_departments": accessible_depts
        }
        self._write_log(self.RAG_LOG_FILE, log_entry)
        
        if self.enable_console:
            self.logger.info("Step 3: RBAC Role Resolution")
            self.logger.info(f"  User Roles: {user_roles}")
            self.logger.info(f"  Effective Roles (with inheritance): {effective_roles}")
            self.logger.info(f"  Effective Permissions: {permissions}")
            self.logger.info(f"  Accessible Departments: {accessible_depts}\n")
    
    def log_retrieval(self, variant_num: int, variant: str, results_count: int, department: str = None):
        """Log vector retrieval results"""
        if self.enable_console:
            dept_info = f" (Department: {department})" if department else ""
            self.logger.info(f"  Retrieving for variant {variant_num}: \"{variant}\"{dept_info}")
            self.logger.info(f"    Retrieved {results_count} candidates")
    
    def log_retrieval_summary(self, total_candidates: int, accessible_depts: List[str]):
        """Log retrieval summary"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "rag_retrieval_summary",
            "total_candidates": total_candidates,
            "accessible_departments": accessible_depts
        }
        self._write_log(self.RAG_LOG_FILE, log_entry)
        
        if self.enable_console:
            self.logger.info(f"  Total candidates retrieved: {total_candidates}")
            self.logger.info(f"  From departments: {accessible_depts}\n")
    
    def log_reranking(self, before_count: int, after_count: int, top_k: int):
        """Log re-ranking results"""
        if self.enable_console:
            self.logger.info("Step 4: Re-ranking & Deduplication")
            self.logger.info(f"  Before re-ranking: {before_count} results")
            self.logger.info(f"  After re-ranking: {after_count} results")
            self.logger.info(f"  Returning top {min(top_k, after_count)} results\n")
    
    def log_final_results(self, results: List[Dict[str, Any]], username: Optional[str] = None):
        """Log final RAG results"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "rag_final_results",
            "username": username,
            "result_count": len(results),
            "result_ids": [r['id'] for r in results]
        }
        self._write_log(self.RAG_LOG_FILE, log_entry)
        
        if self.enable_console:
            self.logger.info("Step 5: Final Results")
            for i, result in enumerate(results, 1):
                dept = result.get('metadata', {}).get('department', 'N/A')
                self.logger.info(
                    f"  {i}. {result['id']} | "
                    f"Dept: {dept} | "
                    f"Similarity: {result['similarity']:.4f}"
                )
    
    def log_query_complete(self, results_count: int):
        """Log query completion"""
        if self.enable_console:
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Pipeline Complete: {results_count} results returned")
            self.logger.info(f"{'='*60}\n")
    
    # ==================== GENERAL LOGGING ====================
    
    def log_error(self, error_type: str, error_msg: str):
        """Log errors"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "error",
            "error_type": error_type,
            "error_message": error_msg
        }
        self._write_log(self.RAG_LOG_FILE, log_entry)
        
        if self.enable_console:
            self.logger.error(f"ERROR [{error_type}]: {error_msg}")
    
    def log_warning(self, warning_msg: str):
        """Log warnings"""
        if self.enable_console:
            self.logger.warning(f"WARNING: {warning_msg}")
    
    def log_info(self, message: str):
        """Log general information"""
        if self.enable_console:
            self.logger.info(message)
    
    def log_component_init(self, component_name: str, details: str = ""):
        """Log component initialization"""
        if self.enable_console:
            detail_str = f" ({details})" if details else ""
            self.logger.info(f"✓ {component_name} initialized{detail_str}")
    
    # ==================== LOG RETRIEVAL ====================
    
    def get_recent_auth_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent authentication logs"""
        try:
            with open(self.AUTH_LOG_FILE, 'r') as f:
                lines = f.readlines()
            
            recent_logs = []
            for line in lines[-limit:]:
                try:
                    recent_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
            
            return list(reversed(recent_logs))
        except FileNotFoundError:
            return []
    
    def get_recent_access_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent access control logs"""
        try:
            with open(self.ACCESS_LOG_FILE, 'r') as f:
                lines = f.readlines()
            
            recent_logs = []
            for line in lines[-limit:]:
                try:
                    recent_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
            
            return list(reversed(recent_logs))
        except FileNotFoundError:
            return []
    
    def get_recent_rag_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent RAG pipeline logs"""
        try:
            with open(self.RAG_LOG_FILE, 'r') as f:
                lines = f.readlines()
            
            recent_logs = []
            for line in lines[-limit:]:
                try:
                    recent_logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
            
            return list(reversed(recent_logs))
        except FileNotFoundError:
            return []
    
    def get_user_activity(self, username: str, limit: int = 20) -> Dict:
        """Get all activity for a specific user"""
        auth_logs = self.get_recent_auth_logs(limit=100)
        access_logs = self.get_recent_access_logs(limit=100)
        rag_logs = self.get_recent_rag_logs(limit=100)
        
        user_auth = [log for log in auth_logs if log.get("username") == username][:limit]
        user_access = [log for log in access_logs if log.get("username") == username][:limit]
        user_rag = [log for log in rag_logs if log.get("username") == username][:limit]
        
        return {
            "username": username,
            "authentication_logs": user_auth,
            "access_logs": user_access,
            "rag_logs": user_rag
        }