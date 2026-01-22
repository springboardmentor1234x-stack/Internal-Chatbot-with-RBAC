from security import hash_password

users_db = {
    "intern": {
        "username": "intern",
        "password": hash_password("intern123"),
        "role": "intern"
    },
    "finance": {
        "username": "finance",
        "password": hash_password("finance123"),
        "role": "finance"
    },
    "admin": {
        "username": "admin",
        "password": hash_password("admin123"),
        "role": "admin"
    }
}
