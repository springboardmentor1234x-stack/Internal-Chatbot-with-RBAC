# 🤖 Company Internal Chatbot with Role-Based Access Control (RBAC)

A secure internal chatbot system that processes natural language queries and retrieves department-specific company information using Retrieval-Augmented Generation (RAG). The system authenticates users, assigns roles, and provides role-based access to company documents stored in a vector database.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Features

- **🔐 Secure Authentication**: JWT-based authentication with role assignment
- **👥 Role-Based Access Control**: Finance, Marketing, HR, Engineering, C-Level, Employee, and Intern roles
- **🤖 RAG Pipeline**: Semantic search with LLM-generated responses
- **📚 Document Processing**: Supports Markdown and CSV documents
- **🎯 Role-Filtered Search**: Users only see documents their role permits
- **💬 Chat Interface**: Streamlit-based web interface
- **📊 Source Attribution**: Responses include source document references

## ⚡ Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup System

```bash
python setup.py
```

### 3. Run Application

```bash
# Single command to start both backend and frontend
python run.py
```

### 4. Access Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs

## 👤 Test Accounts

All test accounts use password: `password123`

| Username | Role | Access Level |
|----------|------|-------------|
| `admin` | Admin | Full system access |
| `clevel_user` | C-Level | All documents |
| `finance_user` | Finance | Finance + General docs |
| `marketing_user` | Marketing | Marketing + General docs |
| `hr_user` | HR | HR + General docs |
| `engineering_user` | Engineering | Engineering + General docs |
| `employee_user` | Employee | General docs only |
| `intern_user` | Intern | General docs only |

## 🚀 Running in VS Code

### Method 1: Press F5 (Debug Mode)
1. Open VS Code in project folder
2. Press `F5`
3. Select `🔥 Run Full Application`

### Method 2: Using Tasks
1. Press `Ctrl+Shift+P`
2. Type: `Tasks: Run Task`
3. Select: `🔥 Start Full Application`

### Method 3: Terminal Commands
```bash
# Backend
python app/main.py

# Frontend (new terminal)
streamlit run frontend/app.py
```

## 📁 Project Structure

```
├── app/                    # Backend application
│   ├── main.py            # FastAPI application
│   ├── routes.py          # API endpoints
│   ├── auth_utils.py      # Authentication utilities
│   ├── database.py        # Database operations
│   ├── rag_pipeline.py    # RAG implementation
│   └── utils/
├── frontend/              # Streamlit interface
│   └── app.py
├── data/                  # Data storage
│   ├── raw/              # Source documents
│   └── chroma/           # Vector database
├── scripts/              # Utility scripts
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
├── setup.py             # Setup script
└── run.py               # Main entry point
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for password security
- **Role-Based Access**: Document access restricted by user role
- **CORS Protection**: Configured for secure cross-origin requests

## 🤝 Contributing

This project was developed by **Sreevidya P S** as part of the FinSolve Internal Chatbot initiative.

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using FastAPI, Streamlit, and LangChain**