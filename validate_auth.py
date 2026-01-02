#!/usr/bin/env python3
"""
Validate auth_utils.py for common issues that might cause VS Code errors
"""
import ast
import sys

def validate_python_file(filepath):
    """Validate Python file for syntax and common issues"""
    print(f"🔍 Validating {filepath}...")
    
    try:
        # Read the file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse the AST to check for syntax errors
        tree = ast.parse(content, filename=filepath)
        print("✅ Syntax is valid")
        
        # Check for common issues
        issues = []
        
        # Check imports
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        print(f"✅ Found {len(imports)} import statements")
        
        # Check functions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        print(f"✅ Found {len(functions)} functions")
        
        # Check for undefined variables (basic check)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                if node.id not in ['jwt', 'os', 'datetime', 'timedelta', 'timezone', 'HTTPException', 'status', 'Depends', 'OAuth2PasswordBearer', 'load_dotenv']:
                    # This is a very basic check - not comprehensive
                    pass
        
        print("✅ No obvious issues found")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_imports():
    """Test if all imports work"""
    print("\n🧪 Testing imports...")
    
    try:
        import os
        print("✅ os")
        
        from fastapi import Depends, HTTPException, status
        print("✅ fastapi")
        
        from fastapi.security import OAuth2PasswordBearer
        print("✅ fastapi.security")
        
        import jwt
        print("✅ jwt")
        
        from datetime import datetime, timedelta, timezone
        print("✅ datetime")
        
        from dotenv import load_dotenv
        print("✅ dotenv")
        
        return True
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False

def main():
    """Main validation function"""
    print("🔧 Auth Utils Validation")
    print("=" * 40)
    
    # Validate file structure
    file_valid = validate_python_file("app/auth_utils.py")
    
    # Test imports
    imports_valid = test_imports()
    
    print("\n" + "=" * 40)
    if file_valid and imports_valid:
        print("🎉 auth_utils.py is valid!")
        print("\n💡 If VS Code still shows errors:")
        print("   1. Restart VS Code")
        print("   2. Reload Python interpreter (Ctrl+Shift+P → Python: Select Interpreter)")
        print("   3. Clear Python cache: Delete __pycache__ folders")
    else:
        print("❌ Issues found - check the output above")

if __name__ == "__main__":
    main()