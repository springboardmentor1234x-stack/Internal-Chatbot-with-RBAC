#!/usr/bin/env python3
"""
VS Code optimized runner for FinSolve Internal Chatbot
This script is designed to work perfectly with VS Code debugging
"""
import subprocess
import sys
import time
import os
import threading
import webbrowser
from pathlib import Path

class VSCodeRunner:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        
    def setup_environment(self):
        """Setup the environment for VS Code"""
        print("🔧 Setting up VS Code environment...")
        
        # Ensure we're in the right directory
        os.chdir(Path(__file__).parent)
        
        # Add current directory to Python path
        current_dir = str(Path(__file__).parent.absolute())
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🐍 Python path: {sys.executable}")
        
    def run_backend(self):
        """Run FastAPI backend with VS Code debugging support"""
        print("🚀 Starting Backend (FastAPI) for VS Code...")
        try:
            # Import and run directly for better debugging
            import uvicorn
            from app.main import app
            
            print("✅ Backend modules imported successfully")
            print("📍 Backend starting at: http://127.0.0.1:8000")
            print("📚 API Docs available at: http://127.0.0.1:8000/docs")
            
            # Run with uvicorn for development
            uvicorn.run(
                app,
                host="127.0.0.1",
                port=8000,
                reload=True,
                log_level="info",
                access_log=True
            )
            
        except ImportError as e:
            print(f"❌ Import error: {e}")
            print("💡 Make sure dependencies are installed: pip install -r requirements.txt")
        except Exception as e:
            print(f"❌ Backend error: {e}")
            
    def run_frontend(self):
        """Run Streamlit frontend with VS Code integration"""
        print("🎨 Starting Frontend (Streamlit) for VS Code...")
        try:
            # Wait for backend to start
            time.sleep(4)
            
            # Test if backend is running
            import requests
            try:
                response = requests.get("http://127.0.0.1:8000/", timeout=5)
                if response.status_code == 200:
                    print("✅ Backend is running and accessible")
                else:
                    print("⚠️ Backend responded but may have issues")
            except:
                print("⚠️ Backend may not be fully ready yet")
            
            print("📍 Frontend starting at: http://localhost:8501")
            
            # Run Streamlit
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", "frontend/app.py",
                "--server.port=8501",
                "--server.address=localhost",
                "--server.headless=false",
                "--browser.gatherUsageStats=false"
            ], check=True)
            
        except KeyboardInterrupt:
            print("\n🛑 Frontend stopped by user")
        except Exception as e:
            print(f"❌ Frontend error: {e}")
            print("💡 Make sure Streamlit is installed: pip install streamlit")
    
    def open_browser(self):
        """Open browser after services start"""
        time.sleep(6)  # Wait for both services to start
        try:
            print("🌐 Opening browser...")
            webbrowser.open("http://localhost:8501")
        except:
            print("⚠️ Could not open browser automatically")
    
    def run_full_application(self):
        """Run both backend and frontend for VS Code debugging"""
        print("🔥 FinSolve Internal Chatbot - VS Code Mode")
        print("=" * 55)
        print("🎯 Optimized for VS Code debugging and development")
        print("📍 Backend: http://127.0.0.1:8000")
        print("📍 Frontend: http://localhost:8501")
        print("📚 API Docs: http://127.0.0.1:8000/docs")
        print("🔧 VS Code: Set breakpoints and debug normally")
        print("⏹️  Press Ctrl+C to stop both services")
        print("=" * 55)
        
        try:
            # Setup environment
            self.setup_environment()
            
            # Start backend in separate thread for debugging
            backend_thread = threading.Thread(
                target=self.run_backend, 
                name="Backend-Thread",
                daemon=True
            )
            backend_thread.start()
            
            # Start browser opener
            browser_thread = threading.Thread(
                target=self.open_browser,
                name="Browser-Thread", 
                daemon=True
            )
            browser_thread.start()
            
            # Run frontend in main thread (better for VS Code debugging)
            self.run_frontend()
            
        except KeyboardInterrupt:
            print("\n👋 Shutting down VS Code application...")
        finally:
            print("✅ VS Code session ended!")

def main():
    """Main entry point for VS Code"""
    runner = VSCodeRunner()
    runner.run_full_application()

if __name__ == "__main__":
    main()