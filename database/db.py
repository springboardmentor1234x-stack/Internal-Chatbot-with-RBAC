from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./auth.db"

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


# -----------------------------
# DB Initialization (IMPORTANT)
# -----------------------------
def init_db():
    """
    Creates all database tables
    """
    import database.models  # 🔥 VERY IMPORTANT
    Base.metadata.create_all(bind=engine)