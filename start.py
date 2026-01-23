#!/usr/bin/env python3
"""
Main startup script for FinSolve Chatbot
Organized project structure - starts the full system with audit features
"""
import subprocess
import sys
import os

def main():
    """Main startup function"""
    print("🤖 FinSolve Internal Chatbot - Organized Project")
    print("=" * 50)
    print("🎯 Starting with organized project structure...")
    print("📁 All files are now properly organized in folders")
    print("📊 Audit system enabled for login and document tracking")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("scripts/start_with_audit.py"):
        print("❌ Error: Please run this script from the project root directory")
        print("💡 Make sure you're in the finsolve-chatbot folder")
        return
    
    # Run the organized startup script
    try:
        print("🚀 Launching organized FinSolve system...")
        subprocess.run([sys.executable, "scripts/start_with_audit.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 FinSolve stopped by user")
    except FileNotFoundError:
        print("❌ Error: Startup script not found")
        print("💡 Try: python scripts/start_with_audit.py")
    except Exception as e:
        print(f"❌ Error starting FinSolve: {e}")
        print("💡 Try running: python scripts/start_with_audit.py")

if __name__ == "__main__":
    main()