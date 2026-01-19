from data.database.db import Base, engine
from data.database.models import audit_log 

# IMPORTANT: import models so SQLAlchemy sees them
from data.database.models.user import User
from data.database.models.role import Role


def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()