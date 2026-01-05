#!/usr/bin/env python3
"""
Verification script to confirm __pycache__ cleanup was successful
"""

import os
import subprocess
import sys

def check_pycache_folders():
    """Check for any remaining __pycache__ folders in project"""
    print("🔍 Checking for __pycache__ folders...")
    
    pycache_folders = []
    for root, dirs, files in os.walk('.'):
        # Skip .venv directory
        if '.venv' in root:
            continue
        
        if '__pycache__' in dirs:
            pycache_folders.append(os.path.join(root, '__pycache__'))
    
    if pycache_folders:
        print("❌ Found remaining __pycache__ folders:")
        for folder in pycache_folders:
            print(f"   - {folder}")
        return False
    else:
        print("✅ No __pycache__ folders found in project")
        return True

def check_git_status():
    """Check git status for any issues"""
    print("\n🔍 Checking git status...")
    
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️  Git has uncommitted changes:")
            print(result.stdout)
            return False
        else:
            print("✅ Git working tree is clean")
            return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Git status check failed: {e}")
        return False

def test_imports():
    """Test key imports to ensure functionality"""
    print("\n🔍 Testing key imports...")
    
    try:
        # Test enhanced RAG pipeline
        from app.rag_pipeline_enhanced import rag_pipeline
        print("✅ Enhanced RAG pipeline imports successfully")
        
        # Test auth utils
        from app.auth_utils import get_current_user
        print("✅ Auth utils imports successfully")
        
        # Test routes
        from app.routes import router
        print("✅ Routes imports successfully")
        
        # Test database
        from app.database import get_user_from_db
        print("✅ Database imports successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_rag_functionality():
    """Test RAG pipeline functionality"""
    print("\n🔍 Testing RAG pipeline functionality...")
    
    try:
        from app.rag_pipeline_enhanced import rag_pipeline
        
        # Test query
        result = rag_pipeline.run_pipeline("What is the company mission?", "Employee")
        
        if result.get("error"):
            print(f"❌ RAG pipeline error: {result['error']}")
            return False
        
        accuracy = result.get("accuracy_score", 0)
        print(f"✅ RAG pipeline working - Accuracy: {accuracy:.1f}%")
        
        if accuracy >= 70:
            print("✅ Accuracy is within acceptable range")
            return True
        else:
            print("⚠️  Accuracy is below expected range")
            return False
            
    except Exception as e:
        print(f"❌ RAG functionality test failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🧹 FinSolve Chatbot - __pycache__ Cleanup Verification")
    print("=" * 60)
    
    all_checks_passed = True
    
    # Run all checks
    checks = [
        ("__pycache__ Cleanup", check_pycache_folders),
        ("Git Status", check_git_status),
        ("Import Tests", test_imports),
        ("RAG Functionality", test_rag_functionality)
    ]
    
    for check_name, check_func in checks:
        print(f"\n📋 Running {check_name} check...")
        if not check_func():
            all_checks_passed = False
    
    # Final result
    print("\n" + "=" * 60)
    if all_checks_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ __pycache__ cleanup was successful")
        print("✅ Project is ready for development and deployment")
        print("✅ No conflicts or issues detected")
    else:
        print("❌ SOME CHECKS FAILED")
        print("⚠️  Please review the issues above")
    
    print("=" * 60)
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)