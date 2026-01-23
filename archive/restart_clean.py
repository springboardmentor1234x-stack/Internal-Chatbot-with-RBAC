#!/usr/bin/env python3
"""
Clean restart script for FinSolve
"""
import subprocess
import sys
import time
import os

def main():
    print("🧹 Cleaning and restarting FinSolve...")
    
    # Kill any existing processes
    try:
        subprocess.run(["taskkill", "/f", "/im", "python.exe"], capture_output=True)
        print("✅ Killed existing Python processes")
    except:
        pass
    
    time.sleep(2)
    
    # Start backend
    print("🚀 Starting clean backend...")
    backend_process = subprocess.Popen([
        sys.executable, "simple_backend.py"
    ], creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    time.sleep(3)
    
    # Start frontend with clean cache
    print("🎨 Starting clean frontend...")
    frontend_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "frontend/app.py",
        "--server.port=8502", "--global.developmentMode=false"
    ], creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    print("✅ Services restarted!")
    print("🌐 Frontend: http://localhost:8502")
    print("🔧 Backend: http://127.0.0.1:8001")
    
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()