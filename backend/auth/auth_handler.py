import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Optional
from config import Config

class AuthHandler:
    """JWT-based authentication handler with secure token management"""
    
    SECRET_KEY = Config.JWT_SECRET_KEY
    ALGORITHM = Config.ALGORITHM
    
    # Token expiry times
    ACCESS_TOKEN_EXPIRE_MINUTES = Config.ACCESS_TOKEN_EXPIRE_MINUTES
    REFRESH_TOKEN_EXPIRE_DAYS = Config.REFRESH_TOKEN_EXPIRE_DAYS
        
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except ValueError as e:
            # Invalid hash format
            return False
        except Exception:
            return False
    
    def create_access_token(self, username: str, role: str, user_id: int) -> str:
        """Create JWT access token"""
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": username,
            "user_id": user_id,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "token_type": "access"
        }
        
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    
    def create_refresh_token(self, username: str, role: str, user_id: int) -> str:
        """Create JWT refresh token"""
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": username,
            "user_id": user_id,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "token_type": "refresh"
        }
        
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    
    def decode_token(self, token: str) -> Dict:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token")
    
    def get_current_user(self, token: str) -> Optional[Dict]:
        """Extract user information from token"""
        try:
            payload = self.decode_token(token)
            username = payload.get("sub")
            role = payload.get("role")
            user_id = payload.get("user_id")
            
            if username and role:
                return {
                    "username": username,
                    "user_id": user_id,
                    "role": role
                }
            return None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None
    
    def validate_refresh_token(self, token: str) -> Optional[Dict]:
        """Validate refresh token and extract user info"""
        try:
            payload = self.decode_token(token)
            
            # Verify it's a refresh token
            if payload.get("token_type") != "refresh":
                return None
            
            username = payload.get("sub")
            role = payload.get("role")
            user_id = payload.get("user_id")
            
            if username and role:
                return {
                    "username": username,
                    "user_id": user_id,
                    "role": role
                }
            return None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception:
            return None