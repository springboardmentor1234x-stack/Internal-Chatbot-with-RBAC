#!/usr/bin/env python3
"""
Quick test to verify the organized FinSolve system is working
"""
import requests
import time

def test_backend():
    """Test if backend is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running successfully")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running (connection refused)")
        return False
    except Exception as e:
        print(f"❌ Backend test error: {e}")
        return False

def test_frontend():
    """Test if frontend is accessible"""
    try:
        response = requests.get("http://127.0.0.1:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is running successfully")
            return True
        else:
            print(f"❌ Frontend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend is not running (connection refused)")
        return False
    except Exception as e:
        print(f"❌ Frontend test error: {e}")
        return False

def main():
    print("🧪 FinSolve System Test")
    print("=" * 30)
    print("Testing organized project structure...")
    print()
    
    # Test backend
    print("🔧 Testing Backend (http://127.0.0.1:8000)...")
    backend_ok = test_backend()
    
    print()
    
    # Test frontend
    print("🎨 Testing Frontend (http://127.0.0.1:8501)...")
    frontend_ok = test_frontend()
    
    print()
    print("=" * 30)
    
    if backend_ok and frontend_ok:
        print("🎉 All systems are running successfully!")
        print()
        print("🌐 Access your application:")
        print("   • Frontend UI: http://127.0.0.1:8501")
        print("   • Backend API: http://127.0.0.1:8000")
        print("   • API Documentation: http://127.0.0.1:8000/docs")
        print()
        print("👥 Test Users (password: password123):")
        print("   • admin (C-Level) - Full access + audit dashboard")
        print("   • hr_user (HR) - HR access + audit dashboard")
        print("   • finance_user (Finance) - Financial documents")
        print("   • employee (Employee) - General documents")
    elif backend_ok:
        print("⚠️ Backend is running, but frontend needs to be started")
        print("💡 Try: python run.py")
    elif frontend_ok:
        print("⚠️ Frontend is running, but backend needs to be started")
        print("💡 Try: python run.py")
    else:
        print("❌ Neither service is running")
        print("💡 Start the system with: python run.py")

if __name__ == "__main__":
    main()