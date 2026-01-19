#!/usr/bin/env python3
"""
BACKEND ONLY runner for VS Code
Run this in one VS Code terminal
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    print("🚀 Starting FinSolve Backend Server...")
    print("📍 Backend: http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Run the backend using subprocess
        subprocess.run([sys.executable, "app/main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()