#!/usr/bin/env python3
"""
Simple script to run the FastAPI backend from VS Code
"""
import os
import sys
import uvicorn

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("🚀 Starting FinSolve Internal Chatbot Backend...")
    print("📍 Backend will be available at: http://127.0.0.1:8000")
    print("📚 API Documentation: http://127.0.0.1:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    # Run the FastAPI app
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )