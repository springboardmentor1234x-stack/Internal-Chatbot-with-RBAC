from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any

# Import error handling
try:
    from .error_handler import (
        AuthenticationError, AuthorizationError, ValidationError,
        handle_exceptions, safe_execute, logger, ErrorSeverity
    )
except ImportError:
    from error_handler import (
        AuthenticationError, AuthorizationError, ValidationError,
        handle_exceptions, safe_execute, logger, ErrorSeverity
    )

# Configuration
SECRET_KEY = "your_super_secret_key_finsolve_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Role-based permissions
ROLE_PERMISSIONS = {
    "C-Level": ["read:all", "write:all", "admin:all"],
    "Finance": ["read:finance", "read:general", "write:finance"],
    "Marketing": ["read:marketing", "read:general", "write:marketing"],
    "HR": ["read:hr", "read:general", "write:hr"],
    "Engineering": ["read:engineering", "read:general", "write:engineering"],
    "Employee": ["read:general"],
    "Intern": ["read:general", "read:training"],
}


@handle_exceptions(return_dict=False)
def create_token(data: dict, expires_delta: timedelta) -> str:
    """
    Create JWT token with expiration and comprehensive error handling.
    
    Args:
        data: Token payload data
        expires_delta: Token expiration time
        
    Returns:
        Encoded JWT token
        
    Raises:
        AuthenticationError: If token creation fails
    """
    if not data:
        raise ValidationError(
            "Token data cannot be empty",
            details={"data_provided": bool(data)},
            suggestions=["Provide valid token payload data"]
        )
    
    if not expires_delta or expires_delta.total_seconds() <= 0:
        raise ValidationError(
            "Token expiration must be positive",
            details={"expires_delta": str(expires_delta)},
            suggestions=["Provide a positive expiration time"]
        )
    
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        logger.debug(f"Token created successfully for user: {data.get('sub', 'unknown')}")
        return encoded_jwt
        
    except jwt.PyJWTError as e:
        logger.error(f"JWT encoding error: {e}")
        raise AuthenticationError(
            f"Failed to create authentication token: {str(e)}",
            details={"error_type": "jwt_encoding", "algorithm": ALGORITHM},
            suggestions=["Contact system administrator", "Try logging in again"]
        )
    except Exception as e:
        logger.error(f"Unexpected error creating token: {e}")
        raise AuthenticationError(
            f"Token creation failed: {str(e)}",
            details={"error_type": "unexpected"},
            suggestions=["Contact system administrator"]
        )


@handle_exceptions(return_dict=False)
def decode_token(token: str) -> Dict:
    """
    Decode and validate JWT token with comprehensive error handling.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded token payload
        
    Raises:
        AuthenticationError: If token is invalid or expired
    """
    if not token or not token.strip():
        raise AuthenticationError(
            "Authentication token is required",
            details={"token_provided": bool(token)},
            suggestions=["Please log in to get a valid token"]
        )
    
    try:
        payload = jwt.decode(token.strip(), SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate required fields
        username = payload.get("sub")
        if not username:
            raise AuthenticationError(
                "Invalid token: missing user information",
                details={"payload_keys": list(payload.keys())},
                suggestions=["Please log in again to get a valid token"]
            )
        
        logger.debug(f"Token decoded successfully for user: {username}")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise AuthenticationError(
            "Authentication token has expired",
            details={"error_type": "expired_token"},
            suggestions=["Please log in again", "Use refresh token if available"]
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise AuthenticationError(
            f"Invalid authentication token: {str(e)}",
            details={"error_type": "invalid_token"},
            suggestions=["Please log in again", "Check token format"]
        )
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {e}")
        raise AuthenticationError(
            f"Token validation failed: {str(e)}",
            details={"error_type": "unexpected"},
            suggestions=["Contact system administrator"]
        )


@handle_exceptions(return_dict=False)
def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Get current user from JWT token with comprehensive error handling.
    
    Args:
        token: JWT token from request
        
    Returns:
        User information dictionary
        
    Raises:
        HTTPException: For FastAPI compatibility
    """
    try:
        payload = decode_token(token)
        
        username: str = payload.get("sub")
        role: str = payload.get("role")
        
        if not username or not role:
            raise AuthenticationError(
                "Invalid token: incomplete user information",
                details={"has_username": bool(username), "has_role": bool(role)},
                suggestions=["Please log in again"]
            )

        # Add permissions based on role
        permissions = ROLE_PERMISSIONS.get(role, ["read:general"])

        user_info = {
            "username": username, 
            "role": role, 
            "permissions": permissions,
            "token_issued_at": payload.get("iat"),
            "token_expires_at": payload.get("exp")
        }
        
        logger.debug(f"User authenticated: {username} ({role})")
        return user_info
        
    except AuthenticationError as e:
        # Convert to HTTPException for FastAPI
        logger.warning(f"Authentication failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.user_message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


@handle_exceptions(return_dict=False)
def check_permission(user_role: str, required_permission: str) -> bool:
    """
    Check if user role has required permission with validation.
    
    Args:
        user_role: User's role
        required_permission: Required permission string
        
    Returns:
        True if user has permission, False otherwise
        
    Raises:
        ValidationError: If inputs are invalid
    """
    if not user_role or not user_role.strip():
        raise ValidationError(
            "User role cannot be empty",
            details={"user_role": user_role},
            suggestions=["Provide a valid user role"]
        )
    
    if not required_permission or not required_permission.strip():
        raise ValidationError(
            "Required permission cannot be empty",
            details={"required_permission": required_permission},
            suggestions=["Provide a valid permission string"]
        )
    
    user_role = user_role.strip()
    required_permission = required_permission.strip()
    
    try:
        user_permissions = ROLE_PERMISSIONS.get(user_role, [])

        # C-Level has all permissions
        if "admin:all" in user_permissions:
            logger.debug(f"Admin access granted for {user_role}")
            return True

        # Check specific permission
        if required_permission in user_permissions:
            logger.debug(f"Permission granted: {user_role} -> {required_permission}")
            return True

        # Check wildcard permissions
        permission_category = required_permission.split(":")[0]
        if f"{permission_category}:all" in user_permissions:
            logger.debug(f"Wildcard permission granted: {user_role} -> {permission_category}:all")
            return True

        logger.debug(f"Permission denied: {user_role} -> {required_permission}")
        return False
        
    except Exception as e:
        logger.error(f"Error checking permission: {e}")
        # Default to deny access on error
        return False


@handle_exceptions(return_dict=False)
def require_permission(required_permission: str):
    """
    Decorator to require specific permission with enhanced error handling.
    
    Args:
        required_permission: Required permission string
        
    Returns:
        FastAPI dependency function
    """
    if not required_permission:
        raise ValidationError("Required permission cannot be empty")

    def permission_checker(current_user: Dict = Depends(get_current_user)):
        try:
            user_role = current_user.get("role")
            username = current_user.get("username")
            
            if not check_permission(user_role, required_permission):
                logger.warning(f"Access denied for {username} ({user_role}): {required_permission}")
                raise AuthorizationError(
                    f"Access denied: Required permission '{required_permission}'",
                    details={
                        "user_role": user_role,
                        "required_permission": required_permission,
                        "user_permissions": ROLE_PERMISSIONS.get(user_role, [])
                    },
                    suggestions=[
                        f"Contact administrator to request '{required_permission}' permission",
                        "Check if you're using the correct account",
                        f"Required role with this permission: {_get_roles_with_permission(required_permission)}"
                    ]
                )
            
            logger.debug(f"Permission check passed: {username} ({user_role}) -> {required_permission}")
            return current_user
            
        except AuthorizationError as e:
            # Convert to HTTPException for FastAPI
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=e.user_message,
            )
        except Exception as e:
            logger.error(f"Unexpected error in permission check: {e}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    return permission_checker


def _get_roles_with_permission(permission: str) -> List[str]:
    """
    Helper function to get roles that have a specific permission
    """
    roles_with_permission = []
    
    for role, permissions in ROLE_PERMISSIONS.items():
        if permission in permissions or "admin:all" in permissions:
            roles_with_permission.append(role)
        else:
            # Check wildcard permissions
            permission_category = permission.split(":")[0]
            if f"{permission_category}:all" in permissions:
                roles_with_permission.append(role)
    
    return roles_with_permission


@handle_exceptions(return_dict=True)
def validate_token_expiry(token: str) -> Dict[str, Any]:
    """
    Validate token expiry and return time remaining
    
    Args:
        token: JWT token to validate
        
    Returns:
        Dictionary with expiry information
    """
    try:
        payload = decode_token(token)
        
        exp_timestamp = payload.get("exp")
        if not exp_timestamp:
            return {
                "valid": False,
                "error": "Token missing expiration",
                "suggestions": ["Please log in again"]
            }
        
        exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
        current_datetime = datetime.utcnow()
        
        if current_datetime >= exp_datetime:
            return {
                "valid": False,
                "expired": True,
                "error": "Token has expired",
                "suggestions": ["Please log in again", "Use refresh token if available"]
            }
        
        time_remaining = exp_datetime - current_datetime
        
        return {
            "valid": True,
            "expired": False,
            "expires_at": exp_datetime.isoformat(),
            "time_remaining_seconds": int(time_remaining.total_seconds()),
            "time_remaining_minutes": int(time_remaining.total_seconds() // 60)
        }
        
    except AuthenticationError as e:
        return {
            "valid": False,
            "error": e.message,
            "suggestions": e.suggestions
        }
    except Exception as e:
        logger.error(f"Error validating token expiry: {e}")
        return {
            "valid": False,
            "error": "Token validation failed",
            "suggestions": ["Contact system administrator"]
        }
