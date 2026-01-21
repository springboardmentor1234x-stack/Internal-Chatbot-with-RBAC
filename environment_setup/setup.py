"""
Environment setup script for RAG Chatbot project
"""

import subprocess
import sys
import os
from pathlib import Path


def create_project_structure():
    """Create the project directory structure"""
    
    directories = [
        "data",
        "data/raw",
        "data/processed",
        "data/embeddings",
        "config",
        "logs",
        "tests",
        "docs",
        "notebooks"
    ]
    
    print("📁 Creating project structure...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ Created {directory}/")
    
    print("✅ Project structure created!")


def create_env_file():
    """Create a .env template file"""
    
    env_template = """# RAG Chatbot Environment Variables

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=sqlite:///./data/app.db

# Vector Database
VECTOR_DB_TYPE=chroma
CHROMA_PERSIST_DIRECTORY=./data/chroma_db

# LLM Configuration (Choose one)
# OpenAI (Free trial)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Or use HuggingFace
# HUGGINGFACE_API_KEY=your-hf-api-key
# HF_MODEL=meta-llama/Llama-2-7b-chat-hf

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Application Settings
APP_NAME=RAG Chatbot with RBAC
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=INFO

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8501

# Retrieval Settings
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Query Processing
MAX_QUERY_LENGTH=500
ENABLE_QUERY_EXPANSION=True
"""
    
    env_file = Path(".env.template")
    with open(env_file, "w") as f:
        f.write(env_template)
    
    print(f"✅ Created {env_file}")
    print("   📝 Copy this to .env and update with your actual values")


def create_gitignore():
    """Create .gitignore file"""
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
ENV/
env/

# Environment Variables
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Jupyter Notebook
.ipynb_checkpoints

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# Vector Database
data/chroma_db/
data/qdrant_db/

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Data
data/raw/
data/processed/
data/embeddings/
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("✅ Created .gitignore")


def create_readme():
    """Create README.md"""
    
    readme_content = """# RAG Chatbot with Role-Based Access Control (RBAC)

## Overview
A secure internal chatbot system with JWT authentication, role-based access control, and RAG (Retrieval-Augmented Generation) capabilities.

## Features
- 🔐 JWT-based authentication
- 👥 Role-based access control (RBAC)
- 🔍 Semantic search with vector database
- 🤖 LLM-powered responses
- 📚 Document-level source attribution
- 🎯 Department-specific data access

## Project Structure
```
module_1_environment_setup/
├── requirements.txt          # Python dependencies
├── setup.py                 # Environment setup script
├── data_explorer.py         # Data exploration module
├── .env.template           # Environment variables template
├── data/                   # Data storage
├── config/                 # Configuration files
├── logs/                   # Application logs
└── docs/                   # Documentation
```

## Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.template .env
# Edit .env with your configuration
```

### 4. Run Data Explorer
```bash
python data_explorer.py
```

## Roles and Permissions

| Role | Accessible Departments | Permissions |
|------|----------------------|-------------|
| admin | All | read, write, delete, admin |
| c_level | All | read |
| finance_manager | Finance, General | read, write, delete |
| finance_employee | Finance, General | read |
| marketing_manager | Marketing, General | read, write, delete |
| marketing_employee | Marketing, General | read |
| hr_manager | HR, General | read, write, delete |
| hr_employee | HR, General | read |
| engineering_manager | Engineering, General | read, write, delete |
| engineering_employee | Engineering, General | read |
| employee | General | read |

## Testing Module 1

Run the data explorer to verify setup:
```bash
cd module_1_environment_setup
python data_explorer.py
```

Expected output:
- Document summary by department
- Role mappings
- Access control tests
- Generated JSON files

## Next Steps
- Module 2: Document Preprocessing & Metadata Tagging
- Module 3: Vector Database & Embedding Generation

## License
MIT
"""
    
    with open("README.md", "w") as f:
        f.write(readme_content)
    
    print("✅ Created README.md")


def main():
    """Main setup function"""
    print("=" * 60)
    print("RAG CHATBOT - ENVIRONMENT SETUP")
    print("=" * 60)
    
    print("\n🚀 Starting setup...")
    
    # Create project structure
    create_project_structure()
    
    # Create configuration files
    create_env_file()
    create_gitignore()
    create_readme()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n📋 Next Steps:")
    print("   1. Create virtual environment: python -m venv venv")
    print("   2. Activate it: source venv/bin/activate")
    print("   3. Install dependencies: pip install -r requirements.txt")
    print("   4. Copy .env.template to .env and configure")
    print("   5. Run data explorer: python data_explorer.py")
    
    print("\n💡 Quick Start:")
    print("   python setup.py")
    print("   python data_explorer.py")


if __name__ == "__main__":
    main()
