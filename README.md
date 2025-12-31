# Company Internal Chatbot with Role-Based Access Control (RBAC)

A secure internal chatbot system that processes natural language queries and retrieves department-specific company information using Retrieval-Augmented Generation (RAG). The system authenticates users, assigns roles, and provides role-based access to company documents stored in a vector database.

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

### 1. Clone and Setup

```bash
git clone <repository-url>
cd internalchatbot
python setup.py
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Edit `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Start the Application

**Terminal 1 - Backend:**
```bash
python app/main.py
```

**Terminal 2 - Frontend:**
```bash
streamlit run frontend/app.py
```

### 5. Access the Application

- **Frontend**: http://localhost:8501
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

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
internalchatbot/
├── app/
│   ├── main.py              # FastAPI application
│   ├── routes.py            # API endpoints
│   ├── auth_utils.py        # Authentication utilities
│   ├── database.py          # Database operations
│   ├── rag_pipeline.py      # RAG implementation
│   └── utils/
│       └── functions.py     # Helper functions
├── frontend/
│   └── app.py              # Streamlit interface
├── data/
│   ├── raw/                # Source documents
│   └── chroma/             # Vector database
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── setup.py               # Setup script
└── README.md              # This file
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# JWT Configuration
SECRET_KEY=your_super_secret_jwt_key_change_in_production_12345

# Database Configuration
DATABASE_URL=sqlite:///./project.db
```

### Role-Document Mapping

Documents are automatically assigned to roles based on filename:

- `quarterly_financial_report.md` → Finance, C-Level
- `market_report_*.md` → Marketing, C-Level
- `engineering_master_doc.md` → Engineering, C-Level
- `employee_handbook.md` → All roles
- `hr_data.csv` → HR, C-Level

## 🔍 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh token

### Chat
- `POST /api/v1/chat` - Send chat query (requires authentication)
- `GET /api/v1/user/profile` - Get user profile

### Setup
- `GET /api/v1/setup-vector-store` - Initialize vector store

## 🛠️ Development

### Adding New Documents

1. Place documents in `data/raw/` directory
2. Update `DOCUMENT_MAP` in `app/rag_pipeline.py`
3. Restart the application or call `/api/v1/setup-vector-store`

### Adding New Roles

1. Update `ROLE_PERMISSIONS` in `app/auth_utils.py`
2. Add role to `init_database()` in `app/database.py`
3. Update document mappings as needed

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for password security
- **Role-Based Access**: Document access restricted by user role
- **CORS Protection**: Configured for secure cross-origin requests
- **Input Validation**: Pydantic models for request validation

## 🚨 Troubleshooting

### Common Issues

**1. "Cannot connect to backend"**
- Ensure FastAPI is running on http://127.0.0.1:8000
- Check CORS configuration in `app/main.py`

**2. "Vector store not found"**
- Run `python setup.py` to initialize
- Or call `GET /api/v1/setup-vector-store`

**3. "OpenAI API error"**
- Add valid `OPENAI_API_KEY` to `.env` file
- System works without OpenAI but with limited responses

**4. "Authentication failed"**
- Use correct test account credentials
- Check JWT token expiration (30 minutes default)

### Logs and Debugging

- Backend logs appear in terminal running `python app/main.py`
- Enable debug mode by setting `DEBUG=True` in `.env`
- Check browser console for frontend errors

## 📈 Performance

- **Response Time**: < 3 seconds for RAG queries
- **Concurrent Users**: Supports multiple simultaneous users
- **Document Limit**: Tested with 100+ documents
- **Vector Search**: Sub-second similarity search

## 🔄 Deployment

### Production Considerations

1. **Security**:
   - Change `SECRET_KEY` in production
   - Use environment-specific `.env` files
   - Enable HTTPS

2. **Database**:
   - Consider PostgreSQL for production
   - Implement database migrations

3. **Scaling**:
   - Use Redis for session storage
   - Deploy with Docker/Kubernetes
   - Add load balancing

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "app/main.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review API documentation at http://127.0.0.1:8000/docs
- Create an issue in the repository

---

**Built with ❤️ using FastAPI, Streamlit, and LangChain**