#!/usr/bin/env python3
"""
Run both backend and frontend together
Single command to start the entire FinSolve Internal Chatbot application
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
        # Change to the correct directory
        os.chdir(Path(__file__).parent)
        
        # Run the backend
        subprocess.run([
            sys.executable, "app/main.py"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped by user")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def run_frontend():
    """Run the Streamlit frontend"""
    print("🎨 Starting Frontend (Streamlit)...")
    try:
        # Wait a bit for backend to start
        time.sleep(3)
        
        # Change to the correct directory
        os.chdir(Path(__file__).parent)
        
        # Run the frontend
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
    print("🔥 Starting FinSolve Internal Chatbot")
    print("=" * 50)
    print("📍 Backend will be at: http://127.0.0.1:8000")
    print("📍 Frontend will be at: http://localhost:8501")
    print("📚 API Docs will be at: http://127.0.0.1:8000/docs")
    print("⏹️  Press Ctrl+C to stop both services")
    print("=" * 50)
    
    try:
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Start frontend in main thread (so Ctrl+C works properly)
        run_frontend()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down both services...")
        print("✅ Application stopped successfully!")

if __name__ == "__main__":
    main()