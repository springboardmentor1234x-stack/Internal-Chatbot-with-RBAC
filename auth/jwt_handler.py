from datetime import datetime, timedelta
from jose import jwt, JWTError

# -------------------------------------------------
# JWT CONFIGURATION
# -------------------------------------------------
SECRET_KEY = "CHANGE_THIS_SECRET_IN_PRODUCTION"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# -------------------------------------------------
# CREATE TOKEN
# -------------------------------------------------
def create_token(subject: str, role: str, token_type: str, expires_delta: timedelta):
    payload = {
        "sub": subject,
        "role": role,
        "type": token_type,
        "exp": datetime.utcnow() + expires_delta
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_access_token(subject: str, role: str):
    return create_token(
        subject=subject,
        role=role,
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(subject: str, role: str):
    return create_token(
        subject=subject,
        role=role,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

# -------------------------------------------------
# VERIFY TOKEN
# -------------------------------------------------
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
