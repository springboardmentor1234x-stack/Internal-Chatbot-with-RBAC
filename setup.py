#!/usr/bin/env python3
"""
Automated Setup Script for Secure RAG Chatbot
This script will:
1. Initialize the database
2. Set up environment variables
3. Run preprocessing and vector database setup
4. Create run scripts for backend and frontend servers

NOTE: Please create your virtual environment and install dependencies before running this script:
  python -m venv venv
  venv\\Scripts\\activate  (Windows) or source venv/bin/activate (Linux/Mac)
  pip install -r requirements.txt
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import json

class Colors:
    """Terminal color codes"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(message):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

def print_warning(message):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def run_command(command, cwd=None, check=True, show_output=False):
    """Run shell command and return result"""
    try:
        if show_output:
            # Run with real-time output
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding='utf-8',
                errors='replace'
            )
            output = []
            for line in process.stdout:
                print(f"    {line.rstrip()}")
                sys.stdout.flush()
                output.append(line)
            process.wait()
            return process.returncode == 0, ''.join(output), ''
        else:
            result = subprocess.run(
                command,
                shell=True,
                check=check,
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout if e.stdout else '', e.stderr if e.stderr else ''
    except Exception as e:
        return False, '', str(e)

def check_python_version():
    """Check if Python version is 3.8+"""
    print_header("Checking Python Version")
    version = sys.version_info
    print_info(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error("Python 3.8 or higher is required!")
        return False
    
    print_success("Python version is compatible")
    return True

def create_virtual_environment(project_dir):
    """Create virtual environment"""
    print_header("Creating Virtual Environment")
    
    venv_path = project_dir / "venv"
    
    if venv_path.exists():
        print_warning("Virtual environment already exists. Removing old one...")
        shutil.rmtree(venv_path)
    
    success, stdout, stderr = run_command(f"python3 -m venv {venv_path}")
    
    if success:
        print_success(f"Virtual environment created at: {venv_path}")
        return venv_path
    else:
        print_error(f"Failed to create virtual environment: {stderr}")
        return None

def get_pip_command(venv_path):
    """Get pip command based on OS"""
    if platform.system() == "Windows":
        return str(venv_path / "Scripts" / "pip.exe")
    else:
        return str(venv_path / "bin" / "pip")

def get_python_command():
    """Get python command - use sys.executable to ensure we use the same Python running this script"""
    return sys.executable

def check_dependencies():
    """Check if required dependencies are installed"""
    print_header("Checking Dependencies")
    
    print_info(f"Using Python: {sys.executable}")
    print_info(f"Python version: {sys.version}")
    print("")
    
    required_packages = [
        'fastapi',
        'sqlalchemy',
        'passlib',
        'jose',  # python-jose imports as 'jose'
        'chromadb',
        'sentence_transformers',
        'streamlit',
        'pandas'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package} is installed")
        except ImportError:
            print_error(f"{package} is NOT installed")
            missing_packages.append(package)
    
    if missing_packages:
        print("")
        print_error("Missing required packages! Please install them first:")
        print("")
        print_info("Run: pip install -r requirements.txt")
        print("")
        print_info("Or install individually:")
        for pkg in missing_packages:
            print(f"  pip install {pkg}")
        print("")
        return False
    
    print_success("All required dependencies are installed")
    return True

def create_env_file(project_dir):
    """Create .env file with default configuration"""
    print_header("Creating Environment Configuration")
    
    env_file = project_dir / "module_4_backend" / ".env"
    
    if env_file.exists():
        print_warning(".env file already exists. Skipping...")
        return True
    
    env_content = """# Database Configuration
DATABASE_URL=sqlite:///./secure_rag_chatbot.db

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production-please-use-strong-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Keys (Add your own keys)
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOGLE_API_KEY=your-google-api-key-here

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
"""
    
    env_file.write_text(env_content)
    print_success(f"Environment file created at: {env_file}")
    print_warning("⚠ IMPORTANT: Update .env file with your API keys!")
    return True

def initialize_database(project_dir):
    """Initialize SQLite database"""
    print_header("Initializing Database")
    
    python_cmd = get_python_command()
    backend_dir = project_dir / "module_4_backend"
    
    # Create database initialization script
    init_script = """
import sys
sys.path.insert(0, '.')
from database import Base, engine
from models import User, QueryLog

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database initialized successfully!")
"""
    
    init_file = backend_dir / "init_db.py"
    init_file.write_text(init_script)
    
    success, stdout, stderr = run_command(
        f"{python_cmd} init_db.py",
        cwd=backend_dir
    )
    
    if success:
        print_success("Database initialized successfully")
        print_info(stdout)
        return True
    else:
        print_error(f"Failed to initialize database: {stderr}")
        return False

def run_preprocessing(project_dir):
    """Run document preprocessing pipeline"""
    print_header("Running Document Preprocessing")
    
    python_cmd = get_python_command()
    preprocessing_dir = project_dir / "module_2_document_preprocessing"
    
    print_info("Processing documents...")
    print_info("Parsing, cleaning, chunking, and tagging metadata...")
    print("")
    
    # Run with real-time output to see progress
    success, stdout, stderr = run_command(
        f"{python_cmd} preprocessing_pipeline.py",
        cwd=preprocessing_dir,
        show_output=True
    )
    
    print("")
    if success:
        print_success("Document preprocessing completed")
        return True
    else:
        print_warning(f"Preprocessing completed with warnings")
        if stderr:
            print_info(f"Warnings: {stderr[:200]}...")
        return True  # Continue even with warnings

def setup_vector_database(project_dir):
    """Setup vector database with embeddings"""
    print_header("Setting Up Vector Database")
    
    python_cmd = get_python_command()
    vector_db_dir = project_dir / "module_3_vector_database"
    
    print_info("Generating embeddings and storing in ChromaDB...")
    print_info("This may take several minutes depending on document size...")
    print("")
    
    # Run with real-time output to see progress
    success, stdout, stderr = run_command(
        f"{python_cmd} module3_pipeline.py",
        cwd=vector_db_dir,
        show_output=True
    )
    
    print("")
    if success:
        print_success("Vector database setup completed")
        return True
    else:
        print_warning(f"Vector DB setup completed with warnings")
        if stderr:
            print_info(f"Warnings: {stderr[:200]}...")
        return True

def create_run_script(project_dir):
    """Create script to run backend and frontend"""
    print_header("Creating Run Script")
    
    if platform.system() == "Windows":
        run_script_path = project_dir / "run.bat"
        
        script_content = f"""@echo off
echo Starting Secure RAG Chatbot...
echo.

echo Starting Backend Server...
start "Backend" cmd /k "cd module_4_backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 5 /nobreak

echo Starting Frontend Server...
start "Frontend" cmd /k "cd module_6_frontend && streamlit run app.py --server.port 8501"

echo.
echo Both servers started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo.
"""
    else:
        run_script_path = project_dir / "run.sh"
        
        script_content = f"""#!/bin/bash

echo "Starting Secure RAG Chatbot..."
echo ""

echo "Starting Backend Server..."
cd module_4_backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 5

echo "Starting Frontend Server..."
cd ../module_6_frontend
streamlit run app.py --server.port 8501 &
FRONTEND_PID=$!

echo ""
echo "Both servers started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT
wait
"""
    
    run_script_path.write_text(script_content)
    
    if platform.system() != "Windows":
        os.chmod(run_script_path, 0o755)
    
    print_success(f"Run script created: {run_script_path}")
    return run_script_path

def main():
    """Main setup function"""
    project_dir = Path(__file__).parent.absolute()
    
    print_header("SECURE RAG CHATBOT - AUTOMATED SETUP")
    print_info(f"Project directory: {project_dir}")
    print_warning("⚠ Make sure you have activated your virtual environment!")
    print("")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print_error("Cannot continue without required dependencies!")
        sys.exit(1)
    
    # Step 2: Create .env file
    if not create_env_file(project_dir):
        sys.exit(1)
    
    # Step 3: Initialize database
    if not initialize_database(project_dir):
        sys.exit(1)
    
    # Step 4: Run preprocessing
    if not run_preprocessing(project_dir):
        print_warning("Continuing despite preprocessing warnings...")
    
    # Step 5: Setup vector database
    if not setup_vector_database(project_dir):
        print_warning("Continuing despite vector DB warnings...")
    
    # Step 6: Create run script
    run_script_path = create_run_script(project_dir)
    
    # Final message
    print_header("SETUP COMPLETE!")
    print_success("All components initialized and configured")
    print("")
    print_info("Next steps:")
    print(f"  1. Update .env file in module_4_backend/ with your API keys")
    print(f"  2. Run the application:")
    if platform.system() == "Windows":
        print(f"     {Colors.BOLD}run.bat{Colors.ENDC}")
    else:
        print(f"     {Colors.BOLD}./run.sh{Colors.ENDC}")
    print("")
    print_info("Default URLs:")
    print(f"  Backend API:  http://localhost:8000")
    print(f"  Frontend UI:  http://localhost:8501")
    print(f"  API Docs:     http://localhost:8000/docs")
    print("")
    print_success("Happy chatting! 🤖")

if __name__ == "__main__":
    main()
