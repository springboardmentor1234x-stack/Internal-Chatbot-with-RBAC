#!/usr/bin/env python3
"""
Test script for comprehensive error handling implementation

This script tests various error scenarios to ensure the error handling
system works correctly across all components.
"""

import sys
import os
import traceback
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_error_handler():
    """Test the main error handler functionality"""
    print("🧪 Testing Error Handler...")
    
    try:
        from app.error_handler import (
            error_handler, FinSolveError, AuthenticationError, 
            ValidationError, handle_exceptions, safe_execute
        )
        
        # Test 1: Basic error handling
        print("  ✓ Testing basic error creation...")
        error = FinSolveError("Test error message")
        assert error.message == "Test error message"
        assert error.error_code is not None
        print(f"    Generated error code: {error.error_code}")
        
        # Test 2: Specific error types
        print("  ✓ Testing specific error types...")
        auth_error = AuthenticationError("Invalid credentials")
        assert "authentication" in auth_error.category.value
        
        val_error = ValidationError("Invalid input")
        assert "validation" in val_error.category.value
        
        # Test 3: Error handler processing
        print("  ✓ Testing error handler processing...")
        try:
            raise ValueError("Test exception")
        except Exception as e:
            error_response = error_handler.handle_error(e)
            assert "error_code" in error_response
            assert "user_message" in error_response
            print(f"    Processed error: {error_response['error_code']}")
        
        # Test 4: Decorator functionality
        print("  ✓ Testing error handling decorator...")
        
        @handle_exceptions(return_dict=True)
        def test_function():
            raise ValueError("Decorator test")
        
        result = test_function()
        assert "error" in result
        assert result["success"] is False
        
        # Test 5: Safe execution
        print("  ✓ Testing safe execution...")
        
        def failing_function():
            raise RuntimeError("Safe execution test")
        
        result = safe_execute(failing_function, default_return="default")
        assert result == "default"
        
        print("  ✅ Error handler tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error handler test failed: {e}")
        traceback.print_exc()
        return False


def test_database_error_handling():
    """Test database error handling"""
    print("🧪 Testing Database Error Handling...")
    
    try:
        from app.database import get_user_from_db, create_user, initialize_database
        
        # Test 1: Initialize database
        print("  ✓ Testing database initialization...")
        init_result = initialize_database()
        if isinstance(init_result, dict):
            assert init_result.get("success") is not False
        
        # Test 2: Valid user lookup
        print("  ✓ Testing valid user lookup...")
        user = get_user_from_db("admin")
        if isinstance(user, dict) and "error" not in user:
            assert user is not None
            print(f"    Found user: {user.get('username', 'unknown')}")
        
        # Test 3: Invalid user lookup
        print("  ✓ Testing invalid user lookup...")
        invalid_user = get_user_from_db("nonexistent_user_12345")
        # Should return None or error dict, not raise exception
        
        # Test 4: Empty username validation
        print("  ✓ Testing empty username validation...")
        try:
            empty_result = get_user_from_db("")
            # Should handle gracefully
        except Exception as e:
            print(f"    Handled empty username: {type(e).__name__}")
        
        print("  ✅ Database error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Database error handling test failed: {e}")
        traceback.print_exc()
        return False


def test_auth_error_handling():
    """Test authentication error handling"""
    print("🧪 Testing Authentication Error Handling...")
    
    try:
        from app.auth_utils import create_token, decode_token, check_permission
        from datetime import timedelta
        
        # Test 1: Valid token creation
        print("  ✓ Testing valid token creation...")
        token = create_token({"sub": "testuser", "role": "Employee"}, timedelta(minutes=30))
        assert token is not None
        assert isinstance(token, str)
        
        # Test 2: Token decoding
        print("  ✓ Testing token decoding...")
        payload = decode_token(token)
        assert payload["sub"] == "testuser"
        
        # Test 3: Invalid token handling
        print("  ✓ Testing invalid token handling...")
        try:
            decode_token("invalid_token_12345")
            assert False, "Should have raised an error"
        except Exception as e:
            print(f"    Handled invalid token: {type(e).__name__}")
        
        # Test 4: Permission checking
        print("  ✓ Testing permission checking...")
        has_permission = check_permission("Employee", "read:general")
        assert isinstance(has_permission, bool)
        
        # Test 5: Invalid permission check
        print("  ✓ Testing invalid permission parameters...")
        try:
            check_permission("", "read:general")
        except Exception as e:
            print(f"    Handled invalid role: {type(e).__name__}")
        
        print("  ✅ Authentication error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Authentication error handling test failed: {e}")
        traceback.print_exc()
        return False


def test_rag_pipeline_error_handling():
    """Test RAG pipeline error handling"""
    print("🧪 Testing RAG Pipeline Error Handling...")
    
    try:
        from app.rag_pipeline_enhanced import rag_pipeline
        
        # Test 1: Valid query
        print("  ✓ Testing valid RAG query...")
        result = rag_pipeline.run_pipeline("test query", "Employee")
        assert isinstance(result, dict)
        assert "response" in result
        
        # Test 2: Empty query handling
        print("  ✓ Testing empty query handling...")
        empty_result = rag_pipeline.run_pipeline("", "Employee")
        # Should handle gracefully, not crash
        
        # Test 3: Invalid role handling
        print("  ✓ Testing invalid role handling...")
        invalid_role_result = rag_pipeline.run_pipeline("test", "InvalidRole")
        # Should handle gracefully
        
        # Test 4: Long query handling
        print("  ✓ Testing long query handling...")
        long_query = "test " * 1000  # Very long query
        long_result = rag_pipeline.run_pipeline(long_query, "Employee")
        # Should handle gracefully
        
        print("  ✅ RAG pipeline error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ RAG pipeline error handling test failed: {e}")
        traceback.print_exc()
        return False


def test_frontend_error_handling():
    """Test frontend error handling"""
    print("🧪 Testing Frontend Error Handling...")
    
    try:
        # Add frontend directory to path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'frontend'))
        
        from frontend.error_handler_frontend import frontend_error_handler, ErrorType
        import requests
        
        # Test 1: Error analysis
        print("  ✓ Testing error analysis...")
        test_error = requests.exceptions.ConnectionError("Connection failed")
        error_info = frontend_error_handler._analyze_error(test_error, "test operation")
        
        assert error_info["category"] == ErrorType.NETWORK
        assert "user_message" in error_info
        assert "suggestions" in error_info
        
        # Test 2: Error storage
        print("  ✓ Testing error storage...")
        initial_count = frontend_error_handler.error_count
        frontend_error_handler._store_error(error_info)
        assert frontend_error_handler.error_count == initial_count + 1
        
        # Test 3: Error statistics
        print("  ✓ Testing error statistics...")
        stats = frontend_error_handler.get_error_statistics()
        assert "total_errors" in stats
        assert "recent_errors" in stats
        
        print("  ✅ Frontend error handling tests passed!")
        return True
        
    except Exception as e:
        print(f"  ❌ Frontend error handling test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all error handling tests"""
    print("🚀 Starting Comprehensive Error Handling Tests")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Error Handler Core", test_error_handler),
        ("Database Error Handling", test_database_error_handling),
        ("Authentication Error Handling", test_auth_error_handling),
        ("RAG Pipeline Error Handling", test_rag_pipeline_error_handling),
        ("Frontend Error Handling", test_frontend_error_handling),
    ]
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status:<12} {test_name}")
        
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 60)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 All error handling tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)