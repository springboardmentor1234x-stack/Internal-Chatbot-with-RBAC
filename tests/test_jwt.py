from auth.jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token
)

print("=== JWT TEST START ===")

# Simulated user details
subject = "admin@example.com"
role = "admin"

# Create tokens
access_token = create_access_token(subject, role)
refresh_token = create_refresh_token(subject, role)

print("\nACCESS TOKEN:")
print(access_token)

print("\nREFRESH TOKEN:")
print(refresh_token)

# Verify access token
print("\nVERIFY ACCESS TOKEN:")
access_payload = verify_token(access_token)
print(access_payload)

# Verify refresh token
print("\nVERIFY REFRESH TOKEN:")
refresh_payload = verify_token(refresh_token)
print(refresh_payload)

print("\n=== JWT TEST END ===")
