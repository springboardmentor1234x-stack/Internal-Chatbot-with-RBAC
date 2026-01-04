#!/usr/bin/env python3
"""
Basic tests for FinSolve Internal Chatbot
Tests that core components can be imported and initialized
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test that core modules can be imported"""
    try:
        import main
        print("✅ main.py imports successfully")
    except Exception as e:
        print(f"❌ main.py import failed: {e}")
        return False
    
    try:
        import auth_utils
        print("✅ auth_utils.py imports successfully")
    except Exception as e:
        print(f"❌ auth_utils.py import failed: {e}")
        return False
    
    try:
        import routes
        print("✅ routes.py imports successfully")
    except Exception as e:
        print(f"❌ routes.py import failed: {e}")
        return False
    
    try:
        import database
        print("✅ database.py imports successfully")
    except Exception as e:
        print(f"❌ database.py import failed: {e}")
        return False
    
    return True

def test_auth_functions():
    """Test that auth functions work"""
    try:
        from auth_utils import create_token, check_permission
        from datetime import timedelta
        
        # Test token creation
        token = create_token({"sub": "test", "role": "Employee"}, timedelta(minutes=30))
        print("✅ Token creation works")
        
        # Test permission checking
        has_permission = check_permission("C-Level", "read:all")
        assert has_permission == True
        print("✅ Permission checking works")
        
        return True
    except Exception as e:
        print(f"❌ Auth functions test failed: {e}")
        return False

def test_database_functions():
    """Test that database functions work"""
    try:
        from database import get_user_from_db, PWD_CONTEXT
        
        # Test getting a user
        user = get_user_from_db("admin")
        assert user is not None
        print("✅ Database user retrieval works")
        
        # Test password verification
        is_valid = PWD_CONTEXT.verify("password123", user["password_hash"])
        assert is_valid == True
        print("✅ Password verification works")
        
        return True
    except Exception as e:
        print(f"❌ Database functions test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running basic tests for FinSolve Internal Chatbot...")
    print("=" * 60)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_imports()
    all_passed &= test_auth_functions()
    all_passed &= test_database_functions()
    
    print("=" * 60)
    if all_passed:
        print("🎉 All basic tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)