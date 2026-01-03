#!/usr/bin/env python3
"""
Test script for auth_utils.py - Run this in VS Code to verify authentication works
"""
from app.auth_utils import create_token, verify_token, check_permission, ROLE_PERMISSIONS
from datetime import timedelta

def test_token_creation():
    """Test JWT token creation and verification"""
    print("🧪 Testing token creation...")
    
    # Create a test token
    test_data = {"sub": "test_user", "role": "Finance"}
    token = create_token(test_data, timedelta(minutes=5))
    
    print(f"✅ Token created: {token[:50]}...")
    
    # Verify the token
    try:
        decoded = verify_token(token)
        print(f"✅ Token verified: {decoded}")
        return True
    except Exception as e:
        print(f"❌ Token verification failed: {e}")
        return False

def test_permissions():
    """Test role-based permissions"""
    print("\n🧪 Testing permissions...")
    
    test_cases = [
        ("Admin", "read:all", True),
        ("Finance", "read:finance", True),
        ("Finance", "read:marketing", False),
        ("C-Level", "read:finance", True),
        ("Employee", "read:general", True),
        ("Employee", "read:finance", False),
    ]
    
    all_passed = True
    for role, permission, expected in test_cases:
        result = check_permission(role, permission)
        status = "✅" if result == expected else "❌"
        print(f"{status} {role} + {permission} = {result} (expected {expected})")
        if result != expected:
            all_passed = False
    
    return all_passed

def test_role_permissions():
    """Display all role permissions"""
    print("\n📋 Role Permissions Summary:")
    for role, permissions in ROLE_PERMISSIONS.items():
        print(f"  {role}: {', '.join(permissions)}")

def main():
    """Run all authentication tests"""
    print("🔐 Testing FinSolve Authentication System")
    print("=" * 50)
    
    # Test token functionality
    token_test = test_token_creation()
    
    # Test permissions
    permission_test = test_permissions()
    
    # Show role summary
    test_role_permissions()
    
    print("\n" + "=" * 50)
    if token_test and permission_test:
        print("🎉 All authentication tests passed!")
        print("\n💡 Ready to run in VS Code:")
        print("   1. Press F5 to start debugging")
        print("   2. Set breakpoints in auth_utils.py")
        print("   3. Test with: python app/main.py")
    else:
        print("❌ Some tests failed. Check the code above.")

if __name__ == "__main__":
    main()