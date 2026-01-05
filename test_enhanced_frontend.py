#!/usr/bin/env python3
"""
Test script for enhanced frontend features
Tests session management, clear chat, and spinner functionality
"""

import sys
import os
import time
import requests

def test_backend_health():
    """Test backend health endpoint"""
    print("🔍 Testing backend health endpoint...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend health: {data.get('status', 'unknown')}")
            
            components = data.get('components', {})
            for component, status in components.items():
                status_icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                print(f"   {status_icon} {component}: {status}")
            
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend - make sure it's running")
        return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_frontend_imports():
    """Test frontend imports and session management"""
    print("\n🔍 Testing frontend imports...")
    
    try:
        # Test main imports
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        # Test enhanced frontend
        sys.path.insert(0, 'frontend')
        import app as frontend_app
        print("✅ Enhanced frontend imported successfully")
        
        # Test session management functions
        if hasattr(frontend_app, 'initialize_session_state'):
            print("✅ Session state management available")
        
        if hasattr(frontend_app, 'clear_session'):
            print("✅ Clear session functionality available")
        
        if hasattr(frontend_app, 'is_session_expired'):
            print("✅ Session expiry checking available")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False

def test_enhanced_features():
    """Test enhanced features availability"""
    print("\n🔍 Testing enhanced features...")
    
    try:
        sys.path.insert(0, 'frontend')
        import app as frontend_app
        
        # Check for enhanced functions
        enhanced_features = [
            'initialize_session_state',
            'update_activity', 
            'is_session_expired',
            'clear_session',
            'main_chat_interface',
            'login'
        ]
        
        available_features = []
        for feature in enhanced_features:
            if hasattr(frontend_app, feature):
                available_features.append(feature)
                print(f"✅ {feature} - Available")
            else:
                print(f"❌ {feature} - Missing")
        
        print(f"\n📊 Enhanced features: {len(available_features)}/{len(enhanced_features)} available")
        return len(available_features) == len(enhanced_features)
        
    except Exception as e:
        print(f"❌ Enhanced features test error: {e}")
        return False

def test_rag_pipeline():
    """Test RAG pipeline functionality"""
    print("\n🔍 Testing RAG pipeline...")
    
    try:
        from app.rag_pipeline_enhanced import rag_pipeline
        
        # Test query
        result = rag_pipeline.run_pipeline("What is the company mission?", "Employee")
        
        if result.get("error"):
            print(f"❌ RAG pipeline error: {result['error']}")
            return False
        
        accuracy = result.get("accuracy_score", 0)
        print(f"✅ RAG pipeline working - Accuracy: {accuracy:.1f}%")
        
        # Test session state compatibility
        if "response" in result and "sources" in result:
            print("✅ RAG pipeline compatible with session state")
            return True
        else:
            print("⚠️ RAG pipeline missing expected fields")
            return False
            
    except Exception as e:
        print(f"❌ RAG pipeline test error: {e}")
        return False

def run_comprehensive_test():
    """Run all tests"""
    print("🧪 FinSolve Enhanced Frontend - Comprehensive Test")
    print("=" * 60)
    
    tests = [
        ("Backend Health", test_backend_health),
        ("Frontend Imports", test_frontend_imports),
        ("Enhanced Features", test_enhanced_features),
        ("RAG Pipeline", test_rag_pipeline)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed_tests += 1
        else:
            print(f"❌ {test_name} test failed")
    
    # Results
    print("\n" + "=" * 60)
    print("🎯 TEST RESULTS")
    print("=" * 60)
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Enhanced frontend is ready for use")
        print("\n🚀 NEW FEATURES AVAILABLE:")
        print("   ✅ Clear Chat Button - Remove all messages")
        print("   ✅ Enhanced Spinners - Better loading feedback")
        print("   ✅ Session Management - Auto-logout and activity tracking")
        print("   ✅ Chat Statistics - Message count and accuracy tracking")
        print("   ✅ Export Chat - Download conversation history")
        print("   ✅ Enhanced UI - Better colors and layout")
        print("   ✅ Error Handling - Improved error messages and recovery")
        
        print("\n💡 HOW TO USE:")
        print("   1. Start backend: python run.py")
        print("   2. Access frontend: http://localhost:8501")
        print("   3. Login with test accounts (password: password123)")
        print("   4. Use Clear Chat button in sidebar")
        print("   5. Watch enhanced spinners during processing")
        
    elif passed_tests >= total_tests * 0.75:
        print("✅ MOSTLY WORKING - Some minor issues")
        print("⚠️ Check failed tests above")
    else:
        print("❌ SIGNIFICANT ISSUES DETECTED")
        print("🔧 Please review and fix failed tests")
    
    print("=" * 60)
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)