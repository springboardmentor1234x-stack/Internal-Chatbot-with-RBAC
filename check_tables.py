# from data.database.db import engine
# from sqlalchemy import inspect

# inspector = inspect(engine)

# print("Tables in DB:")
# for table in inspector.get_table_names():
#     print("-", table)

# print("\nAudit table columns:")
# for col in inspector.get_columns("audit_logs"):
#     print(col["name"], col["type"])

# from sqlalchemy import inspect
# from data.database.db import engine
# from sqlalchemy import text

# inspector = inspect(engine)

# def show_table_columns(table_name):
#     print(f"\n📌 Columns in '{table_name}' table:")
#     for col in inspector.get_columns(table_name):
#         print(f"- {col['name']} ({col['type']})")

# print("🔥 AUTH DB PATH inspected")

# show_table_columns("users")
# show_table_columns("roles")



# with engine.connect() as conn:
#     result = conn.execute(text("SELECT user_id, username, is_active FROM users"))
#     print("\nUsers in DB:")
#     for row in result:
#         print(row)


from sqlalchemy import create_engine, text
from data.database.db import DATABASE_URL

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("\n📌 Roles in DB:\n")
    result = conn.execute(text("SELECT role_id, role_name FROM roles"))
    for row in result:
        print(f"role_id={row.role_id}, role_name='{row.role_name}'")
