#!/usr/bin/env python3
"""
Startup script for FinSolve with Audit System
Starts both backend and frontend with audit logging enabled
"""
import subprocess
import sys
import os
import time
import threading

def start_backend():
    """Start the FastAPI backend with audit logging"""
    print("🚀 Starting FinSolve Backend with Audit System...")
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up one level from scripts/
    app_dir = os.path.join(project_root, "app")
    
    # Change to app directory
    os.chdir(app_dir)
    
    try:
        # Start the backend server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Backend error: {e}")
    finally:
        # Change back to project root
        os.chdir(project_root)

def start_frontend():
    """Start the Streamlit frontend with audit features"""
    print("🎨 Starting FinSolve Frontend with Audit Dashboard...")
    
    # Get the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)  # Go up one level from scripts/
    frontend_dir = os.path.join(project_root, "frontend")
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    try:
        # Start the frontend server
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app.py", 
            "--server.port", "8501",
            "--server.address", "127.0.0.1"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Frontend error: {e}")
    finally:
        # Change back to project root
        os.chdir(project_root)

def main():
    """Main startup function"""
    print("=" * 60)
    print("🤖 FinSolve Internal Chatbot with Audit System")
    print("=" * 60)
    print()
    print("📊 New Audit Features:")
    print("  • Login tracking with timestamps and IP addresses")
    print("  • Document access logging during queries")
    print("  • Audit dashboard for C-Level and HR users")
    print("  • Comprehensive statistics and reporting")
    print()
    print("🔐 Access Levels:")
    print("  • Regular users: Normal chatbot functionality")
    print("  • C-Level/HR: Additional audit dashboard access")
    print()
    print("🌐 URLs:")
    print("  • Backend API: http://127.0.0.1:8000")
    print("  • Frontend UI: http://127.0.0.1:8501")
    print("  • API Docs: http://127.0.0.1:8000/docs")
    print()
    print("👥 Test Users (password: password123):")
    print("  • admin (C-Level) - Full access + audit dashboard")
    print("  • hr_user (HR) - HR access + audit dashboard")
    print("  • finance_user (Finance) - Financial documents")
    print("  • marketing_user (Marketing) - Marketing documents")
    print("  • employee (Employee) - General documents")
    print("  • intern_user (Intern) - Basic access")
    print()
    print("=" * 60)
    
    # Initialize audit system
    try:
        print("🔧 Initializing audit system...")
        # Add parent directory to path for imports
        import sys
        import os
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        
        from app.audit_logger import initialize_audit_database
        initialize_audit_database()
        print("✅ Audit system initialized successfully")
    except Exception as e:
        print(f"⚠️ Audit system initialization warning: {e}")
        print("   (System will still work, but audit features may be limited)")
    
    print()
    print("🚀 Starting services...")
    print("   Press Ctrl+C to stop both services")
    print()
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(3)
    
    # Start frontend in main thread
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down FinSolve...")
        print("✅ Services stopped successfully")

if __name__ == "__main__":
    main()