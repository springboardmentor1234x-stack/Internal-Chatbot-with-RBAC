from passlib.context import CryptContext
from typing import Optional

# -------------------------------------------------
# Password Hashing Configuration
# -------------------------------------------------
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# -------------------------------------------------
# Hash Password
# -------------------------------------------------
def hash_password(password: str) -> str:
    """
    Hash a plain text password using bcrypt
    """
    if not password:
        raise ValueError("Password cannot be empty")

    return pwd_context.hash(password)

# -------------------------------------------------
# Verify Password
# -------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password
    """
    if not plain_password or not hashed_password:
        return False

    return pwd_context.verify(plain_password, hashed_password)

