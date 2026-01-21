# RAG Chatbot with Role-Based Access Control (RBAC)

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
source venv/bin/activate  # On Windows: venv\Scripts\activate
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
