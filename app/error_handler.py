"""
Comprehensive Error Handling System for FinSolve Application

This module provides centralized error handling, logging, and user-friendly error messages
for the entire application stack including frontend, backend, database, and RAG pipeline.
"""

import logging
import traceback
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
from functools import wraps
import os
import sys

# Configure logging
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Create formatters
detailed_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s'
)
simple_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Configure main logger
logger = logging.getLogger('finsolve')
logger.setLevel(logging.DEBUG)

# File handler for detailed logs
file_handler = logging.FileHandler(f'{LOG_DIR}/finsolve_detailed.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(detailed_formatter)

# File handler for errors only
error_handler = logging.FileHandler(f'{LOG_DIR}/finsolve_errors.log')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(detailed_formatter)

# Console handler for development
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(simple_formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(error_handler)
logger.addHandler(console_handler)


class ErrorCategory(Enum):
    """Error categories for better classification and handling"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATABASE = "database"
    RAG_PIPELINE = "rag_pipeline"
    NETWORK = "network"
    VALIDATION = "validation"
    SYSTEM = "system"
    USER_INPUT = "user_input"
    EXTERNAL_API = "external_api"
    FILE_OPERATION = "file_operation"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FinSolveError(Exception):
    """Base exception class for FinSolve application"""
    
    def __init__(
        self,
        message: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        user_message: str = None,
        error_code: str = None,
        details: Dict[str, Any] = None,
        suggestions: List[str] = None
    ):
        self.message = message
        self.category = category
        self.severity = severity
        self.user_message = user_message or self._generate_user_message()
        self.error_code = error_code or self._generate_error_code()
        self.details = details or {}
        self.suggestions = suggestions or []
        self.timestamp = datetime.now().isoformat()
        
        super().__init__(self.message)
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly error message"""
        user_messages = {
            ErrorCategory.AUTHENTICATION: "Authentication failed. Please check your credentials and try again.",
            ErrorCategory.AUTHORIZATION: "You don't have permission to access this resource.",
            ErrorCategory.DATABASE: "A database error occurred. Please try again later.",
            ErrorCategory.RAG_PIPELINE: "An error occurred while processing your request. Please try rephrasing your question.",
            ErrorCategory.NETWORK: "Network connection error. Please check your internet connection.",
            ErrorCategory.VALIDATION: "Invalid input provided. Please check your data and try again.",
            ErrorCategory.SYSTEM: "A system error occurred. Please try again later.",
            ErrorCategory.USER_INPUT: "Invalid input. Please check your data and try again.",
            ErrorCategory.EXTERNAL_API: "External service error. Please try again later.",
            ErrorCategory.FILE_OPERATION: "File operation failed. Please check file permissions and try again."
        }
        return user_messages.get(self.category, "An unexpected error occurred. Please try again.")
    
    def _generate_error_code(self) -> str:
        """Generate error code for tracking"""
        category_codes = {
            ErrorCategory.AUTHENTICATION: "AUTH",
            ErrorCategory.AUTHORIZATION: "AUTHZ",
            ErrorCategory.DATABASE: "DB",
            ErrorCategory.RAG_PIPELINE: "RAG",
            ErrorCategory.NETWORK: "NET",
            ErrorCategory.VALIDATION: "VAL",
            ErrorCategory.SYSTEM: "SYS",
            ErrorCategory.USER_INPUT: "INPUT",
            ErrorCategory.EXTERNAL_API: "API",
            ErrorCategory.FILE_OPERATION: "FILE"
        }
        
        severity_codes = {
            ErrorSeverity.LOW: "L",
            ErrorSeverity.MEDIUM: "M",
            ErrorSeverity.HIGH: "H",
            ErrorSeverity.CRITICAL: "C"
        }
        
        timestamp_code = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{category_codes.get(self.category, 'UNK')}-{severity_codes.get(self.severity, 'M')}-{timestamp_code}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses"""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "user_message": self.user_message,
            "category": self.category.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp,
            "details": self.details,
            "suggestions": self.suggestions
        }


class AuthenticationError(FinSolveError):
    """Authentication related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class AuthorizationError(FinSolveError):
    """Authorization related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class DatabaseError(FinSolveError):
    """Database related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )


class RAGPipelineError(FinSolveError):
    """RAG Pipeline related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.RAG_PIPELINE,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class ValidationError(FinSolveError):
    """Input validation errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs
        )


class NetworkError(FinSolveError):
    """Network related errors"""
    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.MEDIUM,
            **kwargs
        )


class ErrorHandler:
    """Centralized error handler for the application"""
    
    def __init__(self):
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_severity": {},
            "recent_errors": []
        }
    
    def handle_error(
        self,
        error: Exception,
        context: Dict[str, Any] = None,
        user_id: str = None,
        request_id: str = None
    ) -> Dict[str, Any]:
        """
        Handle any error and return structured response
        
        Args:
            error: The exception that occurred
            context: Additional context information
            user_id: User ID if available
            request_id: Request ID for tracking
            
        Returns:
            Structured error response
        """
        
        # Convert to FinSolveError if needed
        if not isinstance(error, FinSolveError):
            finsolve_error = self._convert_to_finsolve_error(error)
        else:
            finsolve_error = error
        
        # Add context information
        if context:
            finsolve_error.details.update(context)
        
        if user_id:
            finsolve_error.details["user_id"] = user_id
        
        if request_id:
            finsolve_error.details["request_id"] = request_id
        
        # Log the error
        self._log_error(finsolve_error, error)
        
        # Update statistics
        self._update_error_stats(finsolve_error)
        
        # Return structured response
        return finsolve_error.to_dict()
    
    def _convert_to_finsolve_error(self, error: Exception) -> FinSolveError:
        """Convert standard exceptions to FinSolveError"""
        
        error_type = type(error).__name__
        error_message = str(error)
        
        # Map common exceptions to categories
        if "authentication" in error_message.lower() or "login" in error_message.lower():
            return AuthenticationError(f"Authentication failed: {error_message}")
        
        elif "permission" in error_message.lower() or "access denied" in error_message.lower():
            return AuthorizationError(f"Access denied: {error_message}")
        
        elif "database" in error_message.lower() or "sqlite" in error_message.lower():
            return DatabaseError(f"Database error: {error_message}")
        
        elif "network" in error_message.lower() or "connection" in error_message.lower():
            return NetworkError(f"Network error: {error_message}")
        
        elif "validation" in error_message.lower() or "invalid" in error_message.lower():
            return ValidationError(f"Validation error: {error_message}")
        
        else:
            # Default to system error
            return FinSolveError(
                f"{error_type}: {error_message}",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.MEDIUM
            )
    
    def _log_error(self, finsolve_error: FinSolveError, original_error: Exception):
        """Log error with appropriate level"""
        
        log_message = f"[{finsolve_error.error_code}] {finsolve_error.message}"
        
        if finsolve_error.details:
            log_message += f" | Details: {json.dumps(finsolve_error.details, default=str)}"
        
        # Add stack trace for debugging
        if original_error:
            stack_trace = traceback.format_exception(type(original_error), original_error, original_error.__traceback__)
            log_message += f" | Stack trace: {''.join(stack_trace)}"
        
        # Log based on severity
        if finsolve_error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif finsolve_error.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif finsolve_error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
    
    def _update_error_stats(self, error: FinSolveError):
        """Update error statistics"""
        self.error_stats["total_errors"] += 1
        
        # Update category stats
        category = error.category.value
        if category not in self.error_stats["errors_by_category"]:
            self.error_stats["errors_by_category"][category] = 0
        self.error_stats["errors_by_category"][category] += 1
        
        # Update severity stats
        severity = error.severity.value
        if severity not in self.error_stats["errors_by_severity"]:
            self.error_stats["errors_by_severity"][severity] = 0
        self.error_stats["errors_by_severity"][severity] += 1
        
        # Keep recent errors (last 100)
        self.error_stats["recent_errors"].append({
            "error_code": error.error_code,
            "category": category,
            "severity": severity,
            "timestamp": error.timestamp,
            "message": error.message
        })
        
        if len(self.error_stats["recent_errors"]) > 100:
            self.error_stats["recent_errors"] = self.error_stats["recent_errors"][-100:]
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return self.error_stats.copy()
    
    def clear_error_stats(self):
        """Clear error statistics"""
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {},
            "errors_by_severity": {},
            "recent_errors": []
        }


# Global error handler instance
error_handler = ErrorHandler()


def handle_exceptions(
    category: ErrorCategory = ErrorCategory.SYSTEM,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    user_message: str = None,
    return_dict: bool = False
):
    """
    Decorator for automatic exception handling
    
    Args:
        category: Error category
        severity: Error severity
        user_message: Custom user message
        return_dict: Whether to return error dict or raise exception
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Handle the error
                error_response = error_handler.handle_error(
                    e,
                    context={
                        "function": func.__name__,
                        "args": str(args)[:200],  # Limit length
                        "kwargs": str(kwargs)[:200]
                    }
                )
                
                if return_dict:
                    return {"error": error_response, "success": False}
                else:
                    # Re-raise as FinSolveError
                    raise FinSolveError(
                        error_response["message"],
                        category=category,
                        severity=severity,
                        user_message=user_message or error_response["user_message"],
                        error_code=error_response["error_code"],
                        details=error_response["details"]
                    )
        return wrapper
    return decorator


def safe_execute(
    func,
    *args,
    default_return=None,
    log_errors=True,
    **kwargs
):
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        *args: Function arguments
        default_return: Default return value on error
        log_errors: Whether to log errors
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            error_handler.handle_error(
                e,
                context={
                    "function": func.__name__ if hasattr(func, '__name__') else str(func),
                    "safe_execute": True
                }
            )
        return default_return


# Utility functions for common error scenarios
def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Validate that required fields are present in data"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            details={"missing_fields": missing_fields, "provided_fields": list(data.keys())},
            suggestions=[f"Please provide the {field} field" for field in missing_fields]
        )


def validate_user_role(user_role: str, allowed_roles: List[str]) -> None:
    """Validate user role against allowed roles"""
    if user_role not in allowed_roles:
        raise AuthorizationError(
            f"Role '{user_role}' is not authorized for this operation",
            details={"user_role": user_role, "allowed_roles": allowed_roles},
            suggestions=[f"Required role: {' or '.join(allowed_roles)}"]
        )


def validate_input_length(text: str, min_length: int = 1, max_length: int = 10000, field_name: str = "input") -> None:
    """Validate input text length"""
    if len(text) < min_length:
        raise ValidationError(
            f"{field_name} is too short (minimum {min_length} characters)",
            details={"current_length": len(text), "min_length": min_length},
            suggestions=[f"Please provide at least {min_length} characters for {field_name}"]
        )
    
    if len(text) > max_length:
        raise ValidationError(
            f"{field_name} is too long (maximum {max_length} characters)",
            details={"current_length": len(text), "max_length": max_length},
            suggestions=[f"Please limit {field_name} to {max_length} characters"]
        )


# Export main components
__all__ = [
    'ErrorHandler', 'FinSolveError', 'AuthenticationError', 'AuthorizationError',
    'DatabaseError', 'RAGPipelineError', 'ValidationError', 'NetworkError',
    'ErrorCategory', 'ErrorSeverity', 'error_handler', 'handle_exceptions',
    'safe_execute', 'validate_required_fields', 'validate_user_role',
    'validate_input_length', 'logger'
]