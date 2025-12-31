#!/usr/bin/env python3
"""
Simple script to run the Streamlit frontend from VS Code
"""
import os
import sys
import subprocess

if __name__ == "__main__":
    print("🎨 Starting FinSolve Internal Chatbot Frontend...")
    print("📍 Frontend will be available at: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    # Run Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Error running frontend: {e}")
        print("💡 Make sure streamlit is installed: pip install streamlit")