#!/usr/bin/env python3
"""
Test JWT error handling in auth_utils.py
"""
from app.auth_utils import verify_token, get_current_user
import jwt
from datetime import datetime, timedelta, timezone

def test_invalid_tokens():
    """Test various invalid token scenarios"""
    print("🧪 Testing JWT error handling...")
    
    test_cases = [
        ("Invalid token format", "invalid.token.here"),
        ("Empty token", ""),
        ("Expired token", create_expired_token()),
        ("Wrong signature", create_wrong_signature_token()),
        ("Missing claims", create_missing_claims_token()),
    ]
    
    for test_name, token in test_cases:
        try:
            result = verify_token(token)
            print(f"❌ {test_name}: Should have failed but got {result}")
        except Exception as e:
            print(f"✅ {test_name}: Correctly rejected - {type(e).__name__}")

def create_expired_token():
    """Create an expired token for testing"""
    from app.auth_utils import SECRET_KEY, ALGORITHM
    payload = {
        "sub": "test_user",
        "role": "Finance",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1)  # Expired 1 minute ago
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_wrong_signature_token():
    """Create a token with wrong signature"""
    payload = {
        "sub": "test_user", 
        "role": "Finance",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return jwt.encode(payload, "wrong_secret", algorithm="HS256")

def create_missing_claims_token():
    """Create a token missing required claims"""
    from app.auth_utils import SECRET_KEY, ALGORITHM
    payload = {
        "sub": "test_user",
        # Missing "role" claim
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

if __name__ == "__main__":
    test_invalid_tokens()
    print("\n🎉 JWT error handling tests completed!")