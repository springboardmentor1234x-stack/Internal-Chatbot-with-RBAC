# import json
# from pathlib import Path
# from sqlalchemy.orm import Session

# from database.db import SessionLocal
# from database.models.role import Role
# from database.models.user import User
# from auth.auth_utils import hash_password

# # =====================================================
# # Load roles from RBAC (Single Source of Truth)
# # =====================================================

# RBAC_FILE = Path(__file__).resolve().parents[1] / "RBAC" / "rbac.json"

# with open(RBAC_FILE, "r", encoding="utf-8") as f:
#     rbac_data = json.load(f)

# ROLES_FROM_RBAC = list(rbac_data["roles"].keys())

# # =====================================================
# # Seed Database
# # =====================================================

# def seed_data():
#     db: Session = SessionLocal()

#     try:
#         # --------------------------
#         # Insert roles
#         # --------------------------
#         for role_name in ROLES_FROM_RBAC:
#             exists = db.query(Role).filter(Role.role_name == role_name).first()
#             if not exists:
#                 db.add(Role(role_name=role_name))

#         db.commit()

#         # --------------------------
#         # Insert admin user
#         # --------------------------
#         admin_role = db.query(Role).filter(Role.role_name == "admin").first()

#         admin_exists = db.query(User).filter(
#             User.username == "admin@example.com"
#         ).first()

#         if not admin_exists:
#             admin_user = User(
#                 username="admin@example.com",
#                 hashed_password=hash_password("admin123"),
#                 role_id=admin_role.role_id
#             )
#             db.add(admin_user)
#             db.commit()

#         print("✅ Database seeded successfully")

#     finally:
#         db.close()

# from database.db import SessionLocal
# from database.models.role import Role
# from database.models.user import User
# from auth.auth_utils import hash_password


# def seed_db():
#     db = SessionLocal()

#     # ---------------------------
#     # Create Roles
#     # ---------------------------
#     roles = ["intern", "finance", "admin"]
#     role_objects = {}

#     for role_name in roles:
#         role = db.query(Role).filter(Role.role_name == role_name).first()
#         if not role:
#             role = Role(role_name=role_name)
#             db.add(role)
#             db.commit()
#             db.refresh(role)
#         role_objects[role_name] = role

#     # ---------------------------
#     # Create Users
#     # ---------------------------
#     users = [
#         ("intern", "intern123", "intern"),
#         ("finance_employee", "finance123", "finance_employee"),
#         ("admin", "admin123", "admin"),
#     ]

#     for username, password, role_name in users:
#         user = db.query(User).filter(User.username == username).first()
#         if not user:
#             user = User(
#                 username=username,
#                 hashed_password=hash_password(password),
#                 role_id=role_objects[role_name].role_id
#             )
#             db.add(user)

#     db.commit()
#     db.close()
#     print(" Database seeded successfully")

# if __name__ == "__main__":
#     seed_db()


from database.db import SessionLocal
from database.models.role import Role
from database.models.user import User
from auth.auth_utils import hash_password


def seed_db():
    db = SessionLocal()

    # ---------------------------
    # Create Roles
    # ---------------------------
    roles = ["intern", "finance_employee", "admin"]  # include finance_employee correctly
    role_objects = {}

    for role_name in roles:
        role = db.query(Role).filter(Role.role_name == role_name).first()
        if not role:
            role = Role(role_name=role_name)
            db.add(role)
            db.commit()
            db.refresh(role)
        role_objects[role_name] = role

    # ---------------------------
    # Create Users
    # ---------------------------
    users = [
        ("intern_user", "intern123", "intern"),
        ("finance_user", "finance123", "finance_employee"),
        ("admin_user", "admin123", "admin"),
    ]

    for username, password, role_name in users:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(
                username=username,
                hashed_password=hash_password(password),
                role_id=role_objects[role_name].role_id
            )
            db.add(user)

    db.commit()
    db.close()
    print("Database seeded successfully")


if __name__ == "__main__":
    seed_db()
