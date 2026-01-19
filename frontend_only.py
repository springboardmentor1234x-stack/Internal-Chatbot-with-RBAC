#!/usr/bin/env python3
"""
FRONTEND ONLY runner for VS Code
Run this in another VS Code terminal
"""
import subprocess
import sys
import webbrowser
import time

def main():
    print("🎨 Starting FinSolve Frontend...")
    print("📍 Frontend: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Wait a moment then open browser
        time.sleep(2)
        print("🌐 Opening browser...")
        webbrowser.open("http://localhost:8501")
        
        # Start streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()