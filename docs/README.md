# 🤖 FinSolve Internal Chatbot with RBAC - PRESENTATION READY

A sophisticated Role-Based Access Control (RBAC) chatbot system for internal company use, featuring intelligent RAG (Retrieval-Augmented Generation) pipeline, JWT authentication, and advanced analytics.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Presentation](https://img.shields.io/badge/Status-Presentation%20Ready-brightgreen.svg)](#)

## 🎯 **PRESENTATION-READY VERSION**

**🚀 One-Click Demo Startup:**
```bash
# Double-click this file for instant demo
PRESENTATION_STARTUP.bat
```

**📍 Access URLs:**
- **Frontend**: http://localhost:8502
- **Backend API**: http://127.0.0.1:8001  
- **API Documentation**: http://127.0.0.1:8001/docs

**🔑 Demo Accounts** (password: `password123`):
- `admin` - Full access (C-Level) - **Best for demo**
- `finance_user` - Finance reports only
- `marketing_user` - Marketing data only  
- `hr_user` - HR policies only
- `engineering_user` - Technical docs only
- `employee` - Basic access only

## 🚀 Enhanced Features

- **🔐 Advanced Authentication**: JWT-based with refresh tokens and session management
- **👥 Comprehensive RBAC**: 6 distinct roles with granular document permissions
- **🤖 Intelligent RAG Pipeline**: Context-aware responses with accuracy scoring
- **📚 Smart Document Processing**: Multi-format support with relevance ranking
- **🎯 Role-Filtered Access**: Dynamic content filtering based on user permissions
- **💬 Professional Chat Interface**: Real-time chat with analytics dashboard
- **📊 Advanced Analytics**: Chat history, usage statistics, and performance metrics
- **🔍 Source Attribution**: Detailed citations with chunk-level analysis
- **⚡ Real-time Features**: Session management, accuracy tracking, query optimization
- **🎭 Presentation Ready**: Complete demo setup with test accounts and scenarios

## ⚡ Quick Start for Presentation

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