from data.database.db import SessionLocal
from data.database.models.user import User
from data.database.models.role import Role

db = SessionLocal()

print("\n--- ROLES ---")
for role in db.query(Role).all():
    print(role.role_id, role.role_name)

print("\n--- USERS ---")
for user in db.query(User).all():
    print(user.id, user.username, user.role_id)

db.close()

