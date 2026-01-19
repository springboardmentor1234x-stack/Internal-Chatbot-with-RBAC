#!/usr/bin/env python3
"""
VS CODE SETUP for FinSolve Internal Chatbot
Run this once to configure VS Code properly
"""
import os
import json
import subprocess
import sys

def create_vscode_config():
    """Create VS Code configuration files"""
    print("📁 Creating VS Code configuration...")
    
    # Ensure .vscode directory exists
    os.makedirs(".vscode", exist_ok=True)
    
    # Launch configuration
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "🚀 FinSolve Full App",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/run_in_vscode.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}"
            },
            {
                "name": "🔧 Backend Only",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/backend_only.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}"
            },
            {
                "name": "🎨 Frontend Only",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/frontend_only.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}"
            }
        ]
    }
    
    with open(".vscode/launch.json", "w") as f:
        json.dump(launch_config, f, indent=4)
    
    print("✅ VS Code launch configuration created!")

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    
    packages = [
        "fastapi", "uvicorn[standard]", "pydantic", "python-multipart",
        "pyjwt", "passlib[bcrypt]", "python-dotenv", "streamlit", "requests"
    ]
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + packages)
        print("✅ All dependencies installed!")
    except Exception as e:
        print(f"⚠️ Some packages may have failed: {e}")

def test_setup():
    """Test if everything is working"""
    print("🧪 Testing setup...")
    
    try:
        # Test imports
        sys.path.append('app')
        import database
        import auth_utils
        print("✅ Backend imports working!")
        
        import streamlit
        print("✅ Streamlit available!")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    print("🔧 VS Code Setup for FinSolve Internal Chatbot")
    print("=" * 60)
    
    # Step 1: Create VS Code config
    create_vscode_config()
    
    # Step 2: Install dependencies
    install_dependencies()
    
    # Step 3: Test setup
    if test_setup():
        print("\n" + "=" * 60)
        print("✅ VS CODE SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\n🚀 HOW TO RUN IN VS CODE:")
        print("   1. Press F5 in VS Code")
        print("   2. Select '🚀 FinSolve Full App'")
        print("   3. Wait for both services to start")
        print("   4. Browser opens at http://localhost:8501")
        
        print("\n🔧 ALTERNATIVE METHODS:")
        print("   • Terminal: python run_in_vscode.py")
        print("   • Backend only: python backend_only.py")
        print("   • Frontend only: python frontend_only.py")
        
        print("\n🔑 LOGIN CREDENTIALS:")
        print("   Username: admin")
        print("   Password: password123")
        
        print("\n✅ VS CODE IS READY!")
    else:
        print("\n❌ Setup incomplete - check errors above")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()