import sqlite3
import hashlib

def init_db():
    conn = sqlite3.connect("users.db")
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

def create_user(username, password, role):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO users VALUES (?,?,?)",
              (username, hash_pw(password), role))
    conn.commit()
    conn.close()

def authenticate(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT role,password FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if row and row[1] == hash_pw(password):
        return row[0]
    return None
