import jwt
import datetime
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer

SECRET = "infosys_secret"
ALGO = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_token(data, minutes=15):
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes),
        **data
    }
    return jwt.encode(payload, SECRET, algorithm=ALGO)

def decode_token(token):
    try:
        return jwt.decode(token, SECRET, algorithms=[ALGO])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
