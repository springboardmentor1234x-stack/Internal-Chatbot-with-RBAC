from fastapi import FastAPI, Depends, HTTPException
import sqlite3

from backend.auth import create_token, decode_token, oauth2_scheme
from backend.rag import generate_answer

app = FastAPI()

# Connect to users DB
db = sqlite3.connect("users.db", check_same_thread=False)

# Allowed enterprise roles
ALLOWED_ROLES = ["intern", "finance", "hr", "marketing", "engineering", "admin"]


# ---------------- REGISTER ----------------
@app.post("/auth/register")
def register(username: str, password: str, role: str):
    role = role.lower()

    if role not in ALLOWED_ROLES:
        raise HTTPException(status_code=400, detail="Invalid role")

    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (username, password, role)
        )
        db.commit()
        return {"message": "User registered successfully"}
    except:
        raise HTTPException(status_code=400, detail="Username already exists")


# ---------------- LOGIN ----------------
@app.post("/auth/login")
def login(username: str, password: str):
    cur = db.cursor()
    cur.execute(
        "SELECT role FROM users WHERE username=? AND password=?",
        (username, password)
    )
    row = cur.fetchone()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    role = row[0]

    return {
        "access_token": create_token({"sub": username, "role": role}),
        "refresh_token": create_token({"sub": username, "role": role}, 1440)
    }


# ---------------- REFRESH TOKEN ----------------
@app.post("/auth/refresh")
def refresh(token: str):
    data = decode_token(token)
    return {"access_token": create_token(data)}


# ---------------- SEARCH ----------------
@app.get("/search")
def search(q: str, token: str = Depends(oauth2_scheme)):
    try:
        user = decode_token(token)
        role = user["role"]

        answer, sources = generate_answer(q, role)

        return {
            "status": "success",
            "role": role,
            "answer": answer,
            "sources": sources
        }

    except HTTPException as e:
        return {
            "status": "error",
            "code": e.status_code,
            "detail": e.detail
        }

    except Exception as e:
        return {
            "status": "error",
            "code": 500,
            "detail": str(e)
        }
