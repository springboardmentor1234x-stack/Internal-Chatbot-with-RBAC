#!/usr/bin/env python3
"""
VS CODE RUNNER for FinSolve Internal Chatbot
Run this directly in VS Code terminal or with F5
"""
import subprocess
import sys
import time
import os
import threading
import webbrowser
from pathlib import Path

def run_backend():
    """Run the backend server"""
    print("🚀 Starting Backend Server...")
    try:
        # Change to app directory and run main.py
        os.chdir(Path(__file__).parent / "app")
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")
    except Exception as e:
        print(f"❌ Backend error: {e}")
    finally:
        # Change back to root directory
        os.chdir(Path(__file__).parent)

def run_frontend():
    """Run the frontend server"""
    print("🎨 Starting Frontend...")
    try:
        time.sleep(3)  # Wait for backend
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def main():
    """Main function to run both services in VS Code"""
    print("🔥 FinSolve Internal Chatbot - VS CODE VERSION")
    print("=" * 60)
    print("📍 Backend: http://127.0.0.1:8000")
    print("📍 Frontend: http://localhost:8501")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("🔑 Login: admin/password123")
    print("=" * 60)
    print("⏹️  Press Ctrl+C to stop both services")
    print("=" * 60)
    
    try:
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Give backend time to start
        print("⏳ Waiting for backend to start...")
        time.sleep(5)
        
        # Open browser
        print("🌐 Opening browser...")
        webbrowser.open("http://localhost:8501")
        
        # Start frontend in main thread (this will block)
        run_frontend()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down both services...")
        print("✅ Application stopped successfully!")

if __name__ == "__main__":
    main()