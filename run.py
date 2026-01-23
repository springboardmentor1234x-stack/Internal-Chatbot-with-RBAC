#!/usr/bin/env python3
"""
Simple run script for FinSolve - works from project root
"""
import subprocess
import sys
import os
import threading
import time

def start_backend():
    """Start the backend server"""
    print("🚀 Starting Backend...")
    
    # Get absolute paths from the original working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(script_dir, "app")
    
    if not os.path.exists(app_dir):
        print(f"❌ Error: app directory not found at {app_dir}")
        return
    
    os.chdir(app_dir)
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")
    except Exception as e:
        print(f"❌ Backend error: {e}")
    finally:
        os.chdir(script_dir)

def start_frontend():
    """Start the frontend server"""
    print("🎨 Starting Frontend...")
    
    # Get absolute paths from the original working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(script_dir, "frontend")
    
    if not os.path.exists(frontend_dir):
        print(f"❌ Error: frontend directory not found at {frontend_dir}")
        return
    
    os.chdir(frontend_dir)
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "app.py", 
            "--server.port", "8501",
            "--server.address", "127.0.0.1"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    except Exception as e:
        print(f"❌ Frontend error: {e}")
    finally:
        os.chdir(script_dir)

def main():
    print("🤖 FinSolve Chatbot - Quick Start")
    print("=" * 40)
    print(f"📁 Working directory: {os.getcwd()}")
    print("🌐 Backend: http://127.0.0.1:8000")
    print("🎨 Frontend: http://127.0.0.1:8501")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("app") or not os.path.exists("frontend"):
        print("❌ Error: Please run this script from the project root directory")
        print("💡 Make sure you're in the finsolve-chatbot folder")
        print(f"📁 Current directory: {os.getcwd()}")
        print("📁 Expected files: app/, frontend/, project.db")
        return
    
    print("Press Ctrl+C to stop both services")
    print()
    
    # Start backend in thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Wait for backend to start
    time.sleep(3)
    
    # Start frontend in main thread
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")

if __name__ == "__main__":
    main()