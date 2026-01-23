#!/usr/bin/env python3
"""
Main entry point for FinSolve Internal Chatbot
Run both backend and frontend together
Developed by: Sreevidya P S
"""
import subprocess
import sys
import time
import os
import threading
from pathlib import Path

def run_backend():
    """Run the FastAPI backend"""
    print("🚀 Starting Backend (FastAPI)...")
    try:
        subprocess.run([sys.executable, "app/main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def run_frontend():
    """Run the Streamlit frontend"""
    print("🎨 Starting Frontend (Streamlit)...")
    try:
        time.sleep(3)  # Wait for backend to start
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def main():
    """Main function to run both services"""
    print("🔥 FinSolve Internal Chatbot with RBAC")
    print("👩‍💻 Developed by: Sreevidya P S")
    print("=" * 50)
    print("📍 Backend: http://127.0.0.1:8000")
    print("📍 Frontend: http://localhost:8501")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("⏹️  Press Ctrl+C to stop both services")
    print("=" * 50)
    
    try:
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Start frontend in main thread
        run_frontend()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down both services...")
        print("✅ Application stopped successfully!")

if __name__ == "__main__":
    main()