from fastapi import APIRouter, HTTPException, Form
from users_db import users_db
from security import verify_password, create_access_token, create_refresh_token, verify_token

router = APIRouter()

# ---------------- LOGIN ----------------
@router.post("/auth/login")
def login(
    username: str = Form(...),
    password: str = Form(...)
):
    user = users_db.get(username)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({
        "sub": username,
        "role": user["role"]
    })

    refresh_token = create_refresh_token({
        "sub": username,
        "role": user["role"]
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


# ---------------- REFRESH ----------------
@router.post("/auth/refresh")
def refresh_access_token(refresh_token: str = Form(...)):

    payload = verify_token(refresh_token)

    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({
        "sub": payload["sub"],
        "role": payload["role"]
    })

    return {"access_token": new_access_token}
