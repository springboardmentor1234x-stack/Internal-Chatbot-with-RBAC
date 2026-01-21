import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# --------------------------------------------------
# Absolute path to project root
# --------------------------------------------------
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

# # Force DB into /data/auth.db
# DB_PATH = os.path.join(BASE_DIR, "data", "auth.db")

# DATABASE_URL = f"sqlite:///{DB_PATH}"

# --------------------------------------------------
# Database Configuration (ENV-AWARE)
# --------------------------------------------------
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{os.path.join(BASE_DIR, 'data', 'auth.db')}"
)




engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

# -----------------------------
# DB Session Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


