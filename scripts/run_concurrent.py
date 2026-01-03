#!/usr/bin/env python3
"""
Run backend and frontend concurrently using multiprocessing
More robust than threading approach
"""
import multiprocessing
import subprocess
import sys
import time
import os
import signal
from pathlib import Path

def run_backend():
    """Run FastAPI backend process"""
    print("🚀 Backend process starting...")
    os.chdir(Path(__file__).parent)
    
    try:
        subprocess.run([sys.executable, "app/main.py"], check=True)
    except KeyboardInterrupt:
        print("🛑 Backend process interrupted")
    except Exception as e:
        print(f"❌ Backend error: {e}")

def run_frontend():
    """Run Streamlit frontend process"""
    print("🎨 Frontend process starting...")
    
    # Wait for backend to start
    time.sleep(4)
    
    os.chdir(Path(__file__).parent)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--server.headless=true"
        ], check=True)
    except KeyboardInterrupt:
        print("🛑 Frontend process interrupted")
    except Exception as e:
        print(f"❌ Frontend error: {e}")

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Received interrupt signal. Shutting down...")
    # Terminate all child processes
    for process in multiprocessing.active_children():
        process.terminate()
        process.join(timeout=5)
    sys.exit(0)

def main():
    """Main function using multiprocessing"""
    print("🔥 FinSolve Internal Chatbot - Concurrent Mode")
    print("=" * 55)
    print("📍 Backend: http://127.0.0.1:8000")
    print("📍 Frontend: http://localhost:8501")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("⏹️  Press Ctrl+C to stop both services")
    print("=" * 55)
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Create processes
        backend_process = multiprocessing.Process(target=run_backend, name="Backend")
        frontend_process = multiprocessing.Process(target=run_frontend, name="Frontend")
        
        # Start processes
        backend_process.start()
        frontend_process.start()
        
        print("✅ Both processes started!")
        print("🌐 Opening browser automatically in 5 seconds...")
        
        # Wait for processes to complete
        backend_process.join()
        frontend_process.join()
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    finally:
        # Ensure processes are terminated
        if 'backend_process' in locals() and backend_process.is_alive():
            backend_process.terminate()
            backend_process.join(timeout=5)
        
        if 'frontend_process' in locals() and frontend_process.is_alive():
            frontend_process.terminate()
            frontend_process.join(timeout=5)
        
        print("✅ All processes stopped!")

if __name__ == "__main__":
    # Required for Windows multiprocessing
    multiprocessing.freeze_support()
    main()