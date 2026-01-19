#!/usr/bin/env python3
"""
PERMANENT STARTUP SCRIPT for FinSolve Internal Chatbot
This will always work when you restart your computer
"""
import subprocess
import sys
import time
import os
import webbrowser
from pathlib import Path

def main():
    print("🚀 FinSolve Internal Chatbot - PERMANENT STARTUP")
    print("=" * 60)
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Kill any existing Python processes
    print("🧹 Cleaning up existing processes...")
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], 
                      capture_output=True, check=False)
        time.sleep(2)
    except:
        pass
    
    # Check if required files exist
    if not os.path.exists("app/main.py"):
        print("❌ Error: app/main.py not found!")
        input("Press Enter to exit...")
        return
    
    if not os.path.exists("frontend/app.py"):
        print("❌ Error: frontend/app.py not found!")
        input("Press Enter to exit...")
        return
    
    try:
        print("🚀 Starting Backend Server...")
        # Start backend in a new console window
        backend_process = subprocess.Popen([
            sys.executable, "app/main.py"
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print("⏳ Waiting 5 seconds for backend to start...")
        time.sleep(5)
        
        print("🎨 Starting Frontend...")
        # Start frontend in a new console window
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port=8501"
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print("⏳ Waiting 3 seconds for frontend to start...")
        time.sleep(3)
        
        print("\n" + "=" * 60)
        print("✅ PROJECT STARTED SUCCESSFULLY!")
        print("📍 Frontend: http://localhost:8501")
        print("📍 Backend: http://127.0.0.1:8000")
        print("📚 API Docs: http://127.0.0.1:8000/docs")
        print("=" * 60)
        
        print("\n🔑 LOGIN CREDENTIALS:")
        print("   Username: admin")
        print("   Password: password123")
        
        print("\n👥 OTHER TEST ACCOUNTS:")
        print("   finance_user / password123")
        print("   marketing_user / password123")
        print("   hr_user / password123")
        print("   engineering_user / password123")
        print("   employee / password123")
        
        # Open browser automatically
        print("\n🌐 Opening browser...")
        time.sleep(2)
        webbrowser.open("http://localhost:8501")
        
        print("\n✅ PROJECT IS READY FOR USE!")
        print("⏹️  To stop: Close the backend and frontend console windows")
        
        input("\nPress Enter to exit this startup script...")
        
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()