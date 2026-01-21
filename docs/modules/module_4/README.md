# Module 4: Backend & Authentication

**Secure RAG Chatbot with Role-Based Access Control**

This module implements the FastAPI backend with JWT authentication, SQLite database, RBAC middleware, and integration with the Module 3 vector database for semantic search and retrieval.

---

## 🎯 Features

### Authentication & Security
- ✅ **JWT Authentication** (Access + Refresh tokens)
- ✅ **Password Hashing** (bcrypt)
- ✅ **Token Refresh** mechanism
- ✅ **User Session Management**
- ✅ **Secure API endpoints**

### Role-Based Access Control (RBAC)
- ✅ **6 Roles**: Admin, HR, Finance, Engineering, Marketing, General
- ✅ **Permission System** with hierarchical access
- ✅ **API-Level Authorization** (endpoint protection)
- ✅ **Data-Level Authorization** (document filtering)

### RAG Pipeline Integration
- ✅ **Query Processing & Normalization**
- ✅ **Embedding Generation** (SentenceTransformer)
- ✅ **Vector Database Search** with RBAC filtering
- ✅ **Context-Aware Responses**
- ✅ **Source Attribution** with relevance scores
- ✅ **Query Logging** for audit trail

### Database
- ✅ **SQLite** for user and query logs
- ✅ **SQLAlchemy ORM** with models
- ✅ **Automatic table creation**
- ✅ **Query history tracking**

---

## 📁 Project Structure

```
module_4_backend/
├── main.py                 # FastAPI application & endpoints
├── auth.py                 # JWT authentication logic
├── rbac.py                 # RBAC permissions & rules
├── database.py             # Database connection & session
├── models.py               # SQLAlchemy models (User, QueryLog)
├── schemas.py              # Pydantic schemas for API
├── query_processor.py      # Query normalization pipeline
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── test_backend.py        # Automated test suite
├── chatbot.db             # SQLite database (auto-created)
└── README.md              # This file
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd module_4_backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env and set your SECRET_KEY
# For production, use a strong random key:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start the Backend

```bash
# Run FastAPI server
python main.py

# Or use uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: **http://localhost:8000**

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📡 API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login (get tokens) |
| POST | `/auth/refresh` | Refresh access token |

### Protected Endpoints (Require Authentication)

| Method | Endpoint | Description | Required Permission |
|--------|----------|-------------|-------------------|
| POST | `/query` | RAG query with RBAC | Any authenticated user |
| GET | `/stats` | User statistics | Any authenticated user |
| GET | `/admin/users` | List all users | `manage_users` (Admin only) |

---

## 🔐 Authentication Flow

### 1. Register User
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@company.com",
    "password": "secure_password",
    "role": "Finance"
  }'
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": 1,
  "username": "john_doe",
  "role": "Finance"
}
```

### 2. Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "john_doe",
  "role": "Finance"
}
```

### 3. Make Authenticated Request
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the quarterly financial results?",
    "top_k": 5
  }'
```

---

## 🔍 RAG Query Flow

1. **User sends query** → API validates JWT token
2. **Extract user role** → RBAC permissions loaded
3. **Process query** → Normalize & clean text
4. **Generate embedding** → SentenceTransformer model
5. **Search vector DB** → Filter by user's role permissions
6. **Retrieve documents** → Only from authorized departments
7. **Construct prompt** → Add context to LLM prompt
8. **Generate answer** → Simulated LLM response (or OpenAI in production)
9. **Log query** → Save to database for audit
10. **Return response** → With source attribution

---

## 🛡️ RBAC Permissions

### Role Hierarchy

| Role | Departments Access | Permissions |
|------|-------------------|-------------|
| **Admin** | All (HR, Finance, Engineering, Marketing, General) | `manage_users`, `view_all_data`, `query_documents` |
| **HR** | HR, General | `query_documents` |
| **Finance** | Finance, General | `query_documents` |
| **Engineering** | Engineering, General | `query_documents` |
| **Marketing** | Marketing, General | `query_documents` |
| **General** | General only | `query_documents` |

### Permission Definitions

- **`query_documents`**: Can query the RAG system
- **`view_all_data`**: Can access all departments' data
- **`manage_users`**: Can view and manage users (Admin only)

---

## 📊 Example RAG Query Response

**Request:**
```json
{
  "query": "What is the marketing budget for 2024?",
  "top_k": 3
}
```

**Response:**
```json
{
  "query": "What is the marketing budget for 2024?",
  "processed_query": "what is the marketing budget for 2024",
  "answer": "Based on the available information from Marketing department(s):\n\nThe marketing budget for 2024 is allocated across digital marketing, events, and content creation with a focus on ROI optimization...\n\n(Answer compiled from 3 relevant source(s))",
  "sources": [
    {
      "source_id": "source_1",
      "document_name": "marketing_report_2024.md",
      "department": "Marketing",
      "chunk_index": 2,
      "relevance_score": 0.8542,
      "content_preview": "Marketing Budget 2024: Total allocation is $5M distributed across digital campaigns (40%), events (30%), content creation (20%), and analytics tools (10%)..."
    },
    {
      "source_id": "source_2",
      "document_name": "marketing_report_q1_2024.md",
      "department": "Marketing",
      "chunk_index": 0,
      "relevance_score": 0.7823,
      "content_preview": "Q1 2024 budget execution report: 98% of allocated funds were utilized effectively with strong ROI on digital campaigns..."
    }
  ],
  "metadata": {
    "user_role": "Marketing",
    "documents_found": 3,
    "model_used": "simulated_llm",
    "prompt_tokens": 342,
    "top_k": 3
  }
}
```

---

## 🧪 Testing

### Automated Test Suite

Run the comprehensive test suite:

```bash
python test_backend.py
```

**Tests Include:**
- ✅ Health check
- ✅ User registration (6 roles)
- ✅ User login & token generation
- ✅ RAG queries with RBAC validation
- ✅ User statistics endpoint
- ✅ Admin authorization (positive & negative tests)

**Expected Output:**
```
🚀 Starting Module 4 Backend Tests...
🌐 Backend URL: http://localhost:8000
============================================================

📊 Testing Health Endpoint...
✅ PASS: Health Check
   └─ Status: healthy, Vector DB docs: 70

👤 Testing User Registration...
✅ PASS: Register admin_user
   └─ Role: Admin
✅ PASS: Register hr_user
   └─ Role: HR
...

============================================================
📋 TEST SUMMARY
============================================================
✅ Passed: 25
❌ Failed: 0
📊 Total:  25

🎉 ALL TESTS PASSED!
```

### Manual Testing with cURL

**1. Register a user:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "email": "test@company.com", "password": "test123", "role": "Finance"}'
```

**2. Login:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "test123"}'
```

**3. Query with token:**
```bash
TOKEN="your_access_token_here"
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the financial results?", "top_k": 5}'
```

---

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```env
# JWT Configuration
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=sqlite:///./chatbot.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True
```

### Generate Secure Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🗄️ Database Schema

### User Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);
```

### QueryLog Table
```sql
CREATE TABLE query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    query TEXT NOT NULL,
    processed_query TEXT,
    response TEXT,
    sources_accessed INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

---

## 🔌 Integration with Module 3

The backend seamlessly integrates with Module 3 (Vector Database):

```python
# Import Module 3 components
from module_3_vector_database.vector_db_manager import VectorDBManager
from module_3_vector_database.embedding_generator import EmbeddingGenerator

# Initialize on startup
embedding_generator = EmbeddingGenerator()
vector_db_manager = VectorDBManager(persist_directory='../module_3_vector_database/chroma_db')

# Use in RAG pipeline
query_embedding = embedding_generator.generate_embedding(query)
search_results = vector_db_manager.search(
    query_embedding=query_embedding,
    top_k=5,
    role_filter=user.role  # RBAC filtering
)
```

---

## 📈 Performance & Scalability

### Current Implementation
- **Database**: SQLite (suitable for development/small deployments)
- **Vector DB**: ChromaDB with persistent storage
- **Embedding Model**: `all-MiniLM-L6-v2` (lightweight, fast)
- **Authentication**: Stateless JWT tokens

### Production Recommendations
1. **Database**: Migrate to PostgreSQL for production
2. **Caching**: Add Redis for token blacklisting and caching
3. **LLM Integration**: Replace simulated LLM with OpenAI GPT-4 or similar
4. **Rate Limiting**: Add rate limiting per user/role
5. **Logging**: Integrate structured logging (e.g., Loguru)
6. **Monitoring**: Add Prometheus metrics and health checks
7. **Deployment**: Use Docker + Kubernetes for scalability

---

## 🚨 Security Considerations

### Implemented
✅ Password hashing with bcrypt  
✅ JWT token expiration  
✅ RBAC at API and data levels  
✅ Input validation with Pydantic  
✅ SQL injection protection (SQLAlchemy ORM)  
✅ CORS headers (if needed)  

### Production Checklist
- [ ] Use strong SECRET_KEY (256-bit)
- [ ] Enable HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Add token blacklisting/revocation
- [ ] Enable CORS selectively
- [ ] Add request logging and audit trails
- [ ] Implement password complexity requirements
- [ ] Add 2FA for admin accounts
- [ ] Regular security audits

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if Module 3 vector DB exists
ls -la ../module_3_vector_database/chroma_db/

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python version (requires 3.8+)
python --version
```

### Database errors
```bash
# Delete and recreate database
rm chatbot.db
python main.py  # Will auto-create tables
```

### Authentication errors
```bash
# Check if SECRET_KEY is set in .env
cat .env | grep SECRET_KEY

# Verify token format
echo $TOKEN | cut -d. -f2 | base64 -d
```

### Vector DB search returns no results
```bash
# Verify vector DB has documents
python -c "
from module_3_vector_database.vector_db_manager import VectorDBManager
db = VectorDBManager(persist_directory='../module_3_vector_database/chroma_db')
print(db.collection.count())
"
```

---

## 📚 Dependencies

See `requirements.txt`:
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **sqlalchemy**: ORM for database
- **pydantic**: Data validation
- **python-jose**: JWT tokens
- **passlib**: Password hashing
- **bcrypt**: Password hashing algorithm
- **python-dotenv**: Environment variables
- **sentence-transformers**: Embeddings (from Module 3)
- **chromadb**: Vector database (from Module 3)

---

## 🎓 Module Completion Checklist

- [x] FastAPI application setup
- [x] JWT authentication (access + refresh tokens)
- [x] User registration & login endpoints
- [x] SQLite database with SQLAlchemy
- [x] User and QueryLog models
- [x] RBAC permission system
- [x] API-level authorization middleware
- [x] Data-level authorization (vector DB filtering)
- [x] Query processing & normalization
- [x] Integration with Module 3 vector DB
- [x] RAG pipeline implementation
- [x] Source attribution with relevance scores
- [x] Query logging for audit trail
- [x] User statistics endpoint
- [x] Admin-only endpoints
- [x] Health check endpoint
- [x] Automated test suite
- [x] Environment configuration
- [x] Documentation (README.md)

---

## 🚀 Next Steps

**Module 5: Frontend Development**
- React/Vue.js web interface
- User login & registration UI
- Chat interface for RAG queries
- Source visualization
- User dashboard with stats
- Admin panel for user management

---

## 📝 License

This project is part of the Secure RAG Chatbot implementation.

---

## 👥 Support

For issues or questions:
1. Check this README
2. Run the test suite: `python test_backend.py`
3. Check FastAPI docs: http://localhost:8000/docs
4. Review Module 3 integration

---

**Module 4 Status: ✅ COMPLETE**

Backend is fully implemented with authentication, RBAC, and RAG pipeline integration!
