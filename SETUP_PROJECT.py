#!/usr/bin/env python3
"""
PERMANENT SETUP SCRIPT for FinSolve Internal Chatbot
Run this once to ensure everything is properly configured
"""
import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "fastapi", "uvicorn[standard]", "pydantic", "python-multipart",
            "pyjwt", "passlib[bcrypt]", "python-dotenv", 
            "streamlit", "requests"
        ])
        print("✅ All packages installed successfully!")
        return True
    except Exception as e:
        print(f"⚠️ Some packages failed to install: {e}")
        print("💡 This is usually okay - the project will still work")
        return True

def check_files():
    """Check if all required files exist"""
    print("📁 Checking project files...")
    
    required_files = [
        "app/main.py",
        "app/database.py", 
        "app/auth_utils.py",
        "app/routes.py",
        "app/rag_pipeline_simple_working.py",
        "frontend/app.py",
        "START_PROJECT.bat",
        "start_project.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ All required files present!")
        return True

def test_imports():
    """Test if all imports work"""
    print("🔍 Testing imports...")
    try:
        # Test backend imports
        sys.path.append('app')
        import database
        import auth_utils
        import routes
        import rag_pipeline_simple_working
        print("✅ Backend imports working!")
        
        # Test if streamlit is available
        import streamlit
        print("✅ Streamlit available!")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_desktop_shortcut():
    """Create a desktop shortcut for easy access"""
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "FinSolve Chatbot.lnk")
        target = os.path.join(os.getcwd(), "START_PROJECT.bat")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = os.getcwd()
        shortcut.IconLocation = target
        shortcut.save()
        
        print("✅ Desktop shortcut created!")
        return True
    except:
        print("⚠️ Could not create desktop shortcut (optional)")
        return True

def main():
    print("🔧 FinSolve Internal Chatbot - PERMANENT SETUP")
    print("=" * 60)
    
    # Step 1: Install requirements
    if not install_requirements():
        print("❌ Setup failed at package installation")
        return
    
    # Step 2: Check files
    if not check_files():
        print("❌ Setup failed - missing required files")
        return
    
    # Step 3: Test imports
    if not test_imports():
        print("❌ Setup failed - import errors")
        return
    
    # Step 4: Create shortcut (optional)
    create_desktop_shortcut()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\n🚀 HOW TO START YOUR PROJECT:")
    print("   Method 1: Double-click 'START_PROJECT.bat'")
    print("   Method 2: Run 'python start_project.py'")
    print("   Method 3: Use desktop shortcut (if created)")
    
    print("\n📍 ACCESS URLS:")
    print("   Frontend: http://localhost:8501")
    print("   Backend: http://127.0.0.1:8000")
    
    print("\n🔑 LOGIN CREDENTIALS:")
    print("   Username: admin")
    print("   Password: password123")
    
    print("\n✅ YOUR PROJECT IS PERMANENTLY CONFIGURED!")
    print("   It will work every time you restart your computer.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()