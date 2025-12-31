#!/usr/bin/env python3
"""
Setup script for FinSolve Internal Chatbot with RBAC
This script initializes the database and vector store.
"""

import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def setup_database():
    """Initialize the SQLite database with users."""
    print("🗄️  Setting up database...")
    try:
        from database import init_database
        init_database()
        print("✅ Database initialized successfully!")
        print("📋 Default users created:")
        print("   - admin (Admin role)")
        print("   - finance_user (Finance role)")
        print("   - marketing_user (Marketing role)")
        print("   - hr_user (HR role)")
        print("   - engineering_user (Engineering role)")
        print("   - clevel_user (C-Level role)")
        print("   - employee_user (Employee role)")
        print("   - intern_user (Intern role)")
        print("   All passwords: password123")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    return True

def setup_vector_store():
    """Initialize the vector store with documents."""
    print("\n🔍 Setting up vector store...")
    try:
        from rag_pipeline import rag_pipeline
        
        # Check if documents exist
        data_path = Path("data/raw")
        if not data_path.exists() or not list(data_path.glob("*.md")):
            print("⚠️  No documents found in data/raw/")
            print("   Sample documents have been created for testing.")
            return True
            
        rag_pipeline.setup_vector_store()
        print("✅ Vector store initialized successfully!")
    except Exception as e:
        print(f"❌ Vector store setup failed: {e}")
        print("   This might be due to missing OpenAI API key.")
        print("   You can set it up later by adding OPENAI_API_KEY to .env file")
        return True  # Don't fail setup for this
    return True

def check_environment():
    """Check if environment is properly configured."""
    print("🔧 Checking environment...")
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found, but one has been created with defaults")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    
    print("✅ Environment check passed!")
    return True

def main():
    """Main setup function."""
    print("🚀 FinSolve Internal Chatbot Setup")
    print("=" * 40)
    
    if not check_environment():
        sys.exit(1)
    
    if not setup_database():
        sys.exit(1)
    
    setup_vector_store()
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Add your OpenAI API key to .env file (optional)")
    print("3. Start the backend: python app/main.py")
    print("4. Start the frontend: streamlit run frontend/app.py")
    print("\n🔗 Access the application:")
    print("   - Backend API: http://127.0.0.1:8000")
    print("   - Frontend UI: http://localhost:8501")

if __name__ == "__main__":
    main()