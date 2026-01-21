"""
Module 6 Frontend Testing
Tests the Streamlit interface components and API integration
"""

import requests
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8501"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_backend_connection():
    """Test if backend is running"""
    print_section("Test 1: Backend Connection")
    
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and healthy")
            health = response.json()
            print(f"   LLM Provider: {health.get('llm_provider')}")
            print(f"   Advanced RAG: {health.get('components', {}).get('advanced_rag_pipeline')}")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
        print("   Please start the backend:")
        print("   cd module_4_backend")
        print("   python -m uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_api_endpoints():
    """Test critical API endpoints"""
    print_section("Test 2: API Endpoints")
    
    # Test login
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login",
            json={"username": "alice_finance", "password": "SecurePass123!"}
        )
        
        if response.status_code == 200:
            print("✅ Login endpoint working")
            token = response.json().get('access_token')
            
            # Test basic query
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{BACKEND_URL}/query",
                json={"query": "What is the employee handbook?", "top_k": 3},
                headers=headers
            )
            
            if response.status_code == 200:
                print("✅ Basic query endpoint working")
            else:
                print(f"❌ Basic query failed: {response.status_code}")
            
            # Test advanced query
            response = requests.post(
                f"{BACKEND_URL}/query/advanced",
                json={"query": "What are the financial metrics?", "top_k": 3},
                headers=headers
            )
            
            if response.status_code == 200:
                print("✅ Advanced query endpoint working")
                result = response.json()
                if 'confidence' in result:
                    print(f"   Confidence: {result['confidence'].get('overall_confidence', 0):.2f}%")
            else:
                print(f"❌ Advanced query failed: {response.status_code}")
            
            return True
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
        return False

def check_frontend_port():
    """Check if frontend port is available"""
    print_section("Test 3: Frontend Port Check")
    
    try:
        response = requests.get(f"{FRONTEND_URL}", timeout=2)
        print("⚠️  Port 8501 is already in use")
        print("   Stop any running Streamlit instances:")
        print("   pkill -f streamlit")
        return False
    except requests.exceptions.ConnectionError:
        print("✅ Port 8501 is available")
        return True
    except Exception as e:
        print(f"ℹ️  Port check inconclusive: {e}")
        return True

def print_instructions():
    """Print usage instructions"""
    print_section("Frontend Ready!")
    
    print("""
    🚀 To start the frontend, run:
    
        cd module_6_frontend
        ./start_frontend.sh
    
    Or manually:
    
        streamlit run app.py
    
    📍 Access the app at: http://localhost:8501
    
    🔐 Test Users:
        Username: alice_finance
        Password: SecurePass123!
        Role: Finance Employee
        
        Username: bob_marketing
        Password: SecurePass123!
        Role: Marketing Employee
        
        Username: admin_user
        Password: AdminPass456!
        Role: Admin
    
    ✨ Features to Test:
        1. Login with valid/invalid credentials
        2. Send basic RAG queries
        3. Switch to Advanced RAG mode
        4. View confidence metrics
        5. Expand source documents
        6. Adjust top-K setting
        7. Clear chat history
        8. Logout and re-login
    
    📊 The frontend includes:
        ✓ Beautiful chat interface
        ✓ Role-based access control
        ✓ Confidence scoring display
        ✓ Source document viewer
        ✓ Settings panel
        ✓ User statistics
    """)

def main():
    print("\n" + "█"*80)
    print("  MODULE 6 FRONTEND - PRE-LAUNCH CHECK")
    print("█"*80)
    
    # Run tests
    backend_ok = test_backend_connection()
    
    if backend_ok:
        api_ok = test_api_endpoints()
    else:
        api_ok = False
    
    port_ok = check_frontend_port()
    
    # Summary
    print_section("Summary")
    
    print(f"Backend Connection: {'✅' if backend_ok else '❌'}")
    print(f"API Endpoints: {'✅' if api_ok else '❌'}")
    print(f"Frontend Port: {'✅' if port_ok else '⚠️'}")
    
    if backend_ok and api_ok:
        print("\n🎉 All systems ready! Frontend can be launched.")
        print_instructions()
    else:
        print("\n⚠️  Please fix the issues above before launching frontend.")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
