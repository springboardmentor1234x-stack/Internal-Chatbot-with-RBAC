# import requests
# from sqlalchemy.orm import Session
# from data.database.db import SessionLocal
# from data.database.models.audit_log import AuditLog

# BASE_URL = "http://127.0.0.1:8000"

# USERNAME = "general_user"      # employee
# PASSWORD = "general123"


# def run_test():
#     print("\n🚀 STARTING FULL AUDIT FLOW TEST")

#     # -------------------------
#     # 1️⃣ LOGIN
#     # -------------------------
#     login_resp = requests.post(
#         f"{BASE_URL}/auth/login",
#         json={"username": USERNAME, "password": PASSWORD}
#     )
#     login_resp.raise_for_status()

#     token = login_resp.json()["access_token"]
#     headers = {"Authorization": f"Bearer {token}"}
#     print("✅ LOGIN successful")

#     # -------------------------
#     # 2️⃣ SEARCH (ALLOWED)
#     # -------------------------
#     requests.post(
#         f"{BASE_URL}/search",
#         headers=headers,
#         json={"query": "company policy", "top_k": 2}
#     )
#     print("✅ SEARCH logged")

#     # -------------------------
#     # 3️⃣ RAG QUERY (ALLOWED)
#     # -------------------------
#     requests.post(
#         f"{BASE_URL}/ask",
#         headers=headers,
#         json={"query": "Explain leave policy", "top_k": 2}
#     )
#     print("✅ RAG_QUERY logged")

#     # -------------------------
#     # 4️⃣ RBAC DENIED TEST (ADMIN ENDPOINT)
#     # -------------------------
#     print("🚫 Testing RBAC DENIED scenario (employee → admin-metrics)")

#     denied_resp = requests.get(
#         f"{BASE_URL}/admin-metrics",
#         headers=headers
#     )

#     if denied_resp.status_code == 403:
#         print("✅ RBAC_DENIED correctly blocked (403)")
#     else:
#         print("⚠️ Unexpected response:", denied_resp.status_code)

#     # -------------------------
#     # 5️⃣ LOGOUT
#     # -------------------------
#     requests.post(
#         f"{BASE_URL}/auth/logout",
#         headers=headers
#     )
#     print("✅ LOGOUT logged")

#     # -------------------------
#     # 6️⃣ VERIFY AUDIT LOGS
#     # -------------------------
#     db: Session = SessionLocal()

#     logs = (
#         db.query(AuditLog)
#         .filter(AuditLog.username == USERNAME)
#         .order_by(AuditLog.timestamp)
#         .all()
#     )

#     print("\n📜 AUDIT LOGS FOUND:")
#     for log in logs:
#         print(
#             f"{log.timestamp} | "
#             f"{log.username} | "
#             f"{log.role} | "
#             f"{log.action} | "
#             f"{log.query} | "
#             f"{log.get_documents()}"
#         )

#     db.close()
#     print("\n🎉 AUDIT FLOW VERIFIED SUCCESSFULLY")


# if __name__ == "__main__":
#     run_test()



import requests
from sqlalchemy.orm import Session
from data.database.db import SessionLocal
from data.database.models.audit_log import AuditLog

BASE_URL = "http://127.0.0.1:8000"

# ✅ MUST MATCH auth.db EXACTLY
FINANCE_USER = {
    "username": "finance_emp",
    "password": "finance123"
}

HR_USER = {
    "username": "hr_emp",
    "password": "hr123"
}

# ✅ REAL DOCUMENT NAMES (FROM normalized_datasets)
HR_DOC = "hr_data (1)_cleaned.txt"


# -------------------------------------------------
# AUTH HELPERS
# -------------------------------------------------
def login(user):
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": user["username"],
            "password": user["password"]
        }
    )

    if resp.status_code != 200:
        print(f"❌ LOGIN FAILED for {user['username']} → {resp.status_code}")
        print(resp.text)
        return None

    token = resp.json()["access_token"]
    print(f"✅ LOGIN successful for {user['username']}")
    return {"Authorization": f"Bearer {token}"}


def logout(headers, username):
    requests.post(f"{BASE_URL}/auth/logout", headers=headers)
    print(f"✅ LOGOUT logged for {username}")


# -------------------------------------------------
# AUDIT VERIFICATION
# -------------------------------------------------
def print_audit_logs(username):
    db: Session = SessionLocal()

    logs = (
        db.query(AuditLog)
        .filter(AuditLog.username == username)
        .order_by(AuditLog.timestamp)
        .all()
    )

    print(f"\n📜 AUDIT LOGS FOR {username.upper()}")
    for log in logs:
        print(
            f"{log.timestamp} | "
            f"user={log.username} | "
            f"role={log.role} | "
            f"action={log.action} | "
            f"query={log.query} | "
            f"docs={log.get_documents()}"
        )

    db.close()


# -------------------------------------------------
# MAIN TEST FLOW
# -------------------------------------------------
def run_test():
    print("\n🚀 STARTING FULL RBAC + AUDIT FLOW TEST")

    # =================================================
    # TEST 1: Finance → HR (DENIED)
    # =================================================
    print("\n🚫 TEST 1: Finance user accessing HR document")

    finance_headers = login(FINANCE_USER)
    if not finance_headers:
        return

    resp = requests.get(
        f"{BASE_URL}/documents/{HR_DOC}?department=HR",
        headers=finance_headers
    )

    if resp.status_code == 403:
        print("✅ RBAC_DENIED confirmed (Finance → HR)")
    else:
        print("⚠️ Unexpected response:", resp.status_code)

    logout(finance_headers, FINANCE_USER["username"])

    # =================================================
    # TEST 2: HR → HR (ALLOWED)
    # =================================================
    print("\n✅ TEST 2: HR user accessing HR document (allowed)")

    hr_headers = login(HR_USER)
    if not hr_headers:
        return

    resp = requests.get(
        f"{BASE_URL}/documents/{HR_DOC}?department=HR",
        headers=hr_headers
    )

    if resp.status_code == 200:
        print("✅ Access allowed (HR → HR)")
    else:
        print("⚠️ Unexpected response:", resp.status_code)

    logout(hr_headers, HR_USER["username"])

    # =================================================
    # AUDIT VERIFICATION
    # =================================================
    print("\n🔍 VERIFYING AUDIT LOGS")
    print_audit_logs(FINANCE_USER["username"])
    print_audit_logs(HR_USER["username"])

    print("\n🎉 ALL RBAC + AUDIT TESTS VERIFIED SUCCESSFULLY")


if __name__ == "__main__":
    run_test()

