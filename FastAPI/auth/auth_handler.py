import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, Optional


class AuthHandler:
    # Secret key for JWT signing (In production, use environment variable)
    SECRET_KEY = "your-secret-key-change-this-in-production-use-env-variable"
    ALGORITHM = "HS256"
    
    # Token expiry times
    ACCESS_TOKEN_EXPIRE_MINUTES = 15  # 15 minutes
    REFRESH_TOKEN_EXPIRE_DAYS = 7     # 7 days
    
    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False
    
    def create_access_token(self, username: str, role: str) -> str:
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": username,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "token_type": "access"
        }
        
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    
    def create_refresh_token(self, username: str, role: str) -> str:
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": username,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
            "token_type": "refresh"
        }
        
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
    
    def decode_token(self, token: str) -> Dict:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token")
    
    def get_current_user(self, token: str) -> Optional[Dict]:
        try:
            payload = self.decode_token(token)
            username = payload.get("sub")
            role = payload.get("role")
            
            if username and role:
                return {
                    "username": username,
                    "role": role
                }
            return None
        except Exception:
            return None