#!/usr/bin/env python3
"""
Simple startup script for FinSolve Internal Chatbot
"""
import subprocess
import sys
import time
import os
import webbrowser
from pathlib import Path

def main():
    print("🔥 FinSolve Internal Chatbot Startup")
    print("=" * 50)
    
    # Check if simple_backend.py exists
    if not os.path.exists("simple_backend.py"):
        print("❌ Error: simple_backend.py not found!")
        print("Please make sure you're in the correct directory.")
        input("Press Enter to exit...")
        return
    
    # Check if frontend/app.py exists
    if not os.path.exists("frontend/app.py"):
        print("❌ Error: frontend/app.py not found!")
        print("Please make sure you're in the correct directory.")
        input("Press Enter to exit...")
        return
    
    try:
        print("🚀 Starting Backend Server...")
        # Start backend in a new window
        backend_process = subprocess.Popen([
            sys.executable, "simple_backend.py"
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print("⏳ Waiting 5 seconds for backend to start...")
        time.sleep(5)
        
        print("🎨 Starting Frontend...")
        # Start frontend in a new window
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port=8501"
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print("⏳ Waiting 3 seconds for frontend to start...")
        time.sleep(3)
        
        print("\n" + "=" * 50)
        print("✅ Services Started Successfully!")
        print("📍 Backend: http://127.0.0.1:8000")
        print("📍 Frontend: http://localhost:8501")
        print("📚 API Docs: http://127.0.0.1:8000/docs")
        print("=" * 50)
        
        # Open browser automatically
        print("🌐 Opening browser...")
        webbrowser.open("http://localhost:8501")
        
        print("\n🔑 Test Accounts (password: password123):")
        print("   • admin (C-Level access)")
        print("   • employee (Employee access)")
        print("   • finance_user (Finance access)")
        print("   • marketing_user (Marketing access)")
        print("   • hr_user (HR access)")
        print("   • engineering_user (Engineering access)")
        
        print("\n⏹️  To stop: Close the backend and frontend console windows")
        print("   Or press Ctrl+C in each window")
        
        input("\nPress Enter to exit this startup script...")
        
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()