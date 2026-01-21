from backend.db.user_db import init_db, add_user
from backend.api.auth import hash_password

def seed_users():
    init_db()

    users = [
        ("admin", "admin123", "admin"),
        ("hr", "hr123", "hr"),
        ("finance", "finance123", "finance"),
        ("employee", "emp123", "employee"),

        # 🔹 Additional roles
        ("ceo", "ceo123", "c-level"),
        ("cto", "cto123", "c-level"),
        ("marketing", "market123", "marketing")
    ]

    for username, password, role in users:
        try:
            add_user(
                username=username,
                password=hash_password(password),
                role=role
            )
            print(f"✅ Added user: {username} ({role})")
        except Exception as e:
            print(f"⚠️ User {username} already exists")

if __name__ == "__main__":
    seed_users()
