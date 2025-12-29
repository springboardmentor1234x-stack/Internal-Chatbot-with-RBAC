# import json
# from database.db import Base, engine, SessionLocal
# from database.models.role import Role

# def init_db():
#     # 1. Create tables
#     Base.metadata.create_all(bind=engine)

#     # 2. Load RBAC roles
#     db = SessionLocal()

#     with open("rbac.json") as f:
#         rbac = json.load(f)

#     for role_name in rbac["roles"].keys():
#         exists = db.query(Role).filter_by(role_name=role_name).first()
#         if not exists:
#             db.add(Role(role_name=role_name))

#     db.commit()
#     db.close()

from database.db import Base, engine

# IMPORTANT: import models so SQLAlchemy sees them
from database.models.user import User
from database.models.role import Role


def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    init_db()