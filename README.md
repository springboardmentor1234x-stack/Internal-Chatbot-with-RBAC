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

## 🏗️ Architecture

```
Frontend (Streamlit) → FastAPI Backend → RAG Pipeline → Vector Database (Chroma)
                    ↓
                JWT Authentication → SQLite Database
```

## 📋 Prerequisites

- Python 3.8+
- OpenAI API key (optional, for LLM responses)

## ⚡ Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/finsolve-internal-chatbot.git
cd finsolve-internal-chatbot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup System

```bash
python setup.py
```

### 4. Configure Environment (Optional)

Create `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run Application

```bash
# Single command to start both backend and frontend
python run.py
```

### 6. Access Application

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

## 📁 Project Structure

```
finsolve-internal-chatbot/
├── app/                    # Backend application
│   ├── main.py            # FastAPI application
│   ├── routes.py          # API endpoints
│   ├── auth_utils.py      # Authentication utilities
│   ├── database.py        # Database operations
│   ├── rag_pipeline.py    # RAG implementation
│   └── utils/
│       └── functions.py   # Helper functions
├── frontend/              # Streamlit interface
│   └── app.py
├── data/                  # Data storage
│   ├── raw/              # Source documents
│   └── chroma/           # Vector database
├── scripts/              # Utility scripts
│   ├── run_app.py        # Alternative run script
│   ├── test_auth.py      # Authentication tests
│   └── ...
├── docs/                 # Documentation
│   ├── VS_CODE_GUIDE.md  # VS Code setup guide
│   └── CORRECTIONS_SUMMARY.md
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
├── setup.py             # Setup script
├── run.py               # Main entry point
└── README.md            # This file
```

## 🔧 Development

### Running Individual Components

**Backend only:**
```bash
python app/main.py
```

**Frontend only:**
```bash
streamlit run frontend/app.py
```

### Testing

```bash
# Test authentication
python scripts/test_auth.py

# Test full system
python scripts/test_system.py
```

### Adding New Documents

1. Place documents in `data/raw/` directory
2. Update `DOCUMENT_MAP` in `app/rag_pipeline.py`
3. Restart application or call `/api/v1/setup-vector-store`

### Adding New Roles

1. Update `ROLE_PERMISSIONS` in `app/auth_utils.py`
2. Add role to `init_database()` in `app/database.py`
3. Update document mappings as needed

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for password security
- **Role-Based Access**: Document access restricted by user role
- **CORS Protection**: Configured for secure cross-origin requests
- **Input Validation**: Pydantic models for request validation

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

## 🚨 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.8+ required)
- Install dependencies: `pip install -r requirements.txt`
- Run setup: `python setup.py`

**Frontend won't start:**
- Install Streamlit: `pip install streamlit`
- Check port availability (8501)

**Authentication fails:**
- Use correct credentials (see test accounts above)
- Check JWT token expiration (30 minutes default)

**No search results:**
- Add OpenAI API key to `.env` file
- Initialize vector store: `python setup.py`

## 📈 Performance

- **Response Time**: < 3 seconds for RAG queries
- **Concurrent Users**: Supports multiple simultaneous users
- **Document Limit**: Tested with 100+ documents
- **Vector Search**: Sub-second similarity search

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Check the [troubleshooting section](#-troubleshooting)
- Review [VS Code setup guide](docs/VS_CODE_GUIDE.md)
- Create an issue in the repository

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Frontend powered by [Streamlit](https://streamlit.io/)
- RAG implementation using [LangChain](https://langchain.com/)
- Vector database by [Chroma](https://www.trychroma.com/)

---

**Built with ❤️ for secure internal knowledge management**