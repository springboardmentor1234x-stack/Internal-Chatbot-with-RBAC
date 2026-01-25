import sqlite3
import hashlib

DB = "users.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
    """)
    conn.commit()
    conn.close()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def create_user(u, p, r):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users VALUES (?,?,?)",
              (u, hash_pw(p), r))
    conn.commit()
    conn.close()

def authenticate(u, p):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT role, password FROM users WHERE username=?", (u,))
    row = c.fetchone()
    conn.close()
    if row and row[1] == hash_pw(p):
        return row[0]
    return None
