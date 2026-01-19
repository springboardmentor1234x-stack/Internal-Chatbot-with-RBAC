import os
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError

from backend.auth.token_blacklist import token_blacklist
from data.database.audit import log_action

# -------------------------------------------------
# JWT CONFIGURATION
# -------------------------------------------------
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY not set in environment")

# -------------------------------------------------
# CREATE TOKEN
# -------------------------------------------------
def create_token(
    subject: str,
    role: str,
    user_id: int,
    token_type: str,
    expires_delta: timedelta
):
    now = datetime.now(timezone.utc)

    payload = {
        "sub": subject,
        "role": role,
        "user_id": user_id,
        "type": token_type,  # access | refresh
        "iat": now,
        "exp": now + expires_delta
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(subject: str, role: str, user_id: int):
    return create_token(
        subject=subject,
        role=role,
        user_id=user_id,
        token_type="access",
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )


def create_refresh_token(subject: str, role: str, user_id: int):
    return create_token(
        subject=subject,
        role=role,
        user_id=user_id,
        token_type="refresh",
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

# -------------------------------------------------
# VERIFY TOKEN  🔐 ENTERPRISE-SAFE
# -------------------------------------------------
def verify_token(token: str):
    try:
        # 1️⃣ Decode & validate token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 2️⃣ Check blacklist (logout / forced logout)
        if token_blacklist.is_blacklisted(token):
            _safe_audit(
                username=payload.get("sub"),
                role=payload.get("role"),
                user_id=payload.get("user_id"),
                action="TOKEN_BLACKLISTED"
            )
            return None

        # 3️⃣ Enforce ACCESS token only
        if payload.get("type") != "access":
            _safe_audit(
                username=payload.get("sub"),
                role=payload.get("role"),
                user_id=payload.get("user_id"),
                action="INVALID_TOKEN_TYPE"
            )
            return None

        # ✅ Token valid
        return payload

    except ExpiredSignatureError:
        _safe_audit(
            username="unknown",
            action="TOKEN_EXPIRED"
        )
        return None

    except JWTError:
        _safe_audit(
            username="unknown",
            action="INVALID_TOKEN"
        )
        return None

    except Exception:
        # 🔥 NEVER let auth crash the system
        return None


# -------------------------------------------------
# AUDIT SAFETY WRAPPER (IMPORTANT)
# -------------------------------------------------
def _safe_audit(**kwargs):
    try:
        log_action(**kwargs)
    except Exception:
        pass  # Audit must NEVER break authentication
