from data.database.db import SessionLocal
from data.database.models.role import Role
from data.database.models.user import User
from data.security.passwords import hash_password, verify_password



def seed_db():
    db = SessionLocal()

    roles = [
        "intern", "employee",
        "engineering_employee", "engineering_manager",
        "finance_employee", "finance_manager",
        "hr_employee", "hr_manager",
        "marketing_employee", "marketing_manager",
        "admin", "c_level"
    ]

    role_map = {}

    # Create roles
    for role_name in roles:
        role = db.query(Role).filter(Role.role_name == role_name).first()
        if not role:
            role = Role(role_name=role_name)
            db.add(role)
            db.commit()
            db.refresh(role)
        role_map[role_name] = role

    print("✅ Roles inserted")

    # Create users
    users = [
        ("intern_user", "intern123", "intern"),
        ("general_user", "general123", "employee"),

        ("eng_emp", "eng123", "engineering_employee"),
        ("eng_mgr", "engmgr123", "engineering_manager"),

        ("finance_emp", "finance123", "finance_employee"),
        ("finance_mgr", "finmgr123", "finance_manager"),

        ("hr_emp", "hr123", "hr_employee"),
        ("hr_mgr", "hrmgr123", "hr_manager"),

        ("marketing_emp", "mkt123", "marketing_employee"),
        ("marketing_mgr", "mktmgr123", "marketing_manager"),

        ("admin_user", "admin123", "admin"),
        ("cto_user", "cto123", "c_level"),
    ]

    for username, password, role_name in users:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(
                username=username,
                hashed_password=hash_password(password),
                role_id=role_map[role_name].role_id
            )
            db.add(user)

    db.commit()
    db.close()
    print("✅ Database seeded successfully")


if __name__ == "__main__":
    seed_db()
    