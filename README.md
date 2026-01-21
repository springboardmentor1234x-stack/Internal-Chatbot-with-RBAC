# Secure RAG Chatbot with Role-Based Access Control

A comprehensive enterprise-grade Retrieval-Augmented Generation (RAG) chatbot system with Role-Based Access Control (RBAC). This system enables secure, context-aware conversational AI that respects organizational data access policies.

---

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [User Roles and Permissions](#user-roles-and-permissions)
7. [Setup Instructions](#setup-instructions)
8. [How to Run](#how-to-run)
9. [API Endpoints](#api-endpoints)
10. [Configuration](#configuration)
11. [Module Details](#module-details)

---

## Overview

This project implements a secure RAG chatbot that combines:
- **Retrieval-Augmented Generation (RAG)**: Retrieves relevant documents from a vector database and generates contextual responses using LLMs
- **Role-Based Access Control (RBAC)**: Ensures users can only access documents they are authorized to view based on their department role
- **Multi-LLM Support**: Supports multiple LLM providers including OpenAI, HuggingFace, and local models via Ollama

---

## System Architecture

```
+------------------+       +------------------+       +------------------+
|                  |       |                  |       |                  |
|   Frontend       |<----->|   Backend API    |<----->|   Vector DB      |
|   (Streamlit)    |       |   (FastAPI)      |       |   (ChromaDB)     |
|                  |       |                  |       |                  |
+------------------+       +------------------+       +------------------+
        |                         |                         |
        |                         v                         |
        |                  +------------------+             |
        |                  |                  |             |
        |                  |   LLM Manager    |<------------+
        |                  |   (Multi-Provider)|
        |                  |                  |
        |                  +------------------+
        |                         |
        v                         v
+------------------+       +------------------+
|                  |       |                  |
|   User Auth      |       |   RBAC Engine    |
|   (JWT/SQLite)   |       |   (Permissions)  |
|                  |       |                  |
+------------------+       +------------------+
```

### Data Flow

1. User authenticates via the Streamlit frontend
2. User sends a query to the FastAPI backend
3. Backend validates JWT token and extracts user role
4. Query is embedded using sentence-transformers
5. ChromaDB performs semantic search for relevant documents
6. RBAC engine filters results based on user permissions
7. Filtered documents are re-ranked for relevance
8. LLM generates a response using the context
9. Response with sources and confidence scores is returned to user

---

## Features

| Feature | Description |
|---------|-------------|
| Secure Authentication | JWT-based authentication with access and refresh tokens |
| Role-Based Access Control | Department-level document access restrictions |
| Multi-Provider LLM Support | OpenAI, HuggingFace, and Ollama integration |
| Semantic Search | ChromaDB vector database with sentence-transformer embeddings |
| Document Re-ranking | Cross-encoder based re-ranking for improved relevance |
| Confidence Scoring | Multi-factor confidence assessment for responses |
| Dark/Light Mode UI | Modern, responsive Streamlit interface |
| Query Logging | Track and analyze user queries |
| Suggested Questions | Role-specific question suggestions |

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Backend Framework | FastAPI 0.109.0 |
| Frontend Framework | Streamlit 1.31.0 |
| Database | SQLite with SQLAlchemy 2.0.25 |
| Vector Database | ChromaDB 1.4.1 |
| Embeddings | sentence-transformers 2.3.1 |
| LLM Integration | OpenAI, HuggingFace Hub, Ollama |
| Authentication | python-jose (JWT), bcrypt |
| NLP | tiktoken, transformers 4.37.2 |
| HTTP Client | requests, httpx |
| Server | Uvicorn 0.27.0 |

---

## Project Structure

```
supriya_rag/
|
|-- Dataset/                           # Source documents by department
|   |-- Engineering/                   # Engineering documents
|   |-- Finance/                       # Financial reports and summaries
|   |-- General/                       # Company-wide documents
|   |-- HR/                            # HR data and policies
|   |-- Marketing/                     # Marketing reports
|
|-- environment_setup/                 # Environment configuration
|   |-- setup.py                       # Project setup script
|   |-- config/                        # Configuration files
|   |-- data/                          # Data directories (raw, processed, embeddings)
|
|-- document_preprocessing/            # Document processing pipeline
|   |-- document_parser.py             # Parse various document formats
|   |-- document_chunker.py            # Split documents into chunks (300-512 tokens)
|   |-- text_cleaner.py                # Text normalization and cleaning
|   |-- metadata_tagger.py             # Add RBAC metadata to chunks
|   |-- preprocessing_pipeline.py      # Orchestrate preprocessing
|
|-- vector_database/                   # Vector storage and retrieval
|   |-- embedding_generator.py         # Generate embeddings using sentence-transformers
|   |-- vector_db_manager.py           # ChromaDB operations with RBAC filtering
|   |-- chroma_db/                     # Persisted vector database
|
|-- backend/                           # FastAPI backend server
|   |-- main.py                        # FastAPI application entry point
|   |-- auth.py                        # JWT authentication logic
|   |-- models.py                      # SQLAlchemy database models
|   |-- schemas.py                     # Pydantic request/response schemas
|   |-- rbac.py                        # Role-based access control logic
|   |-- database.py                    # Database configuration
|   |-- query_processor.py             # Query processing utilities
|   |-- .env                           # Environment variables (API keys)
|
|-- llm_integration/                   # LLM and advanced RAG
|   |-- llm_manager.py                 # Multi-provider LLM interface
|   |-- advanced_rag_pipeline.py       # Complete RAG orchestration
|   |-- prompt_templates.py            # LLM prompt templates
|   |-- reranker.py                    # Document re-ranking
|   |-- confidence_scorer.py           # Response confidence scoring
|   |-- response_formatter.py          # Format LLM responses
|   |-- config.py                      # LLM configuration
|
|-- frontend/                          # Streamlit user interface
|   |-- app.py                         # Main Streamlit application
|
|-- docs/                              # Documentation
|-- requirements.txt                   # Python dependencies
|-- run.bat                            # Windows startup script
|-- run.sh                             # Linux/Mac startup script
|-- rbac_permissions.json              # RBAC permission definitions
```

---

## User Roles and Permissions

The system implements a hierarchical RBAC model with the following roles:

| Role | Accessible Departments | Description |
|------|------------------------|-------------|
| admin | Finance, Marketing, HR, Engineering, General | Full access to all documents |
| finance_employee | Finance, General | Access to financial reports and general documents |
| marketing_employee | Marketing, General | Access to marketing reports and general documents |
| hr_employee | HR, General | Access to HR data and general documents |
| engineering_employee | Engineering, General | Access to engineering docs and general documents |
| employee | General | Access to general company documents only |

### RBAC Rules

1. **Deny by Default**: Users cannot access any document unless explicitly permitted
2. **Role-Based Filtering**: Documents are filtered based on user's role during retrieval
3. **Admin Override**: Admin users have access to all departments
4. **Role Union**: Access is granted if user's role matches any of the document's accessible roles

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip package manager
- Git (optional)

### Step 1: Clone or Navigate to Project

```bash
cd supriya_rag
```

### Step 2: Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create or edit the `.env` file in `backend/`:

```env
# Database Configuration
DATABASE_URL=sqlite:///./secure_rag_chatbot.db

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# API Keys (Configure at least one LLM provider)
OPENAI_API_KEY=your-openai-api-key
HUGGINGFACE_API_KEY=your-huggingface-api-key
GOOGLE_API_KEY=your-google-api-key

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_PORT=8501

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_db
```

### Step 5: Initialize Database

The database is automatically initialized when the backend starts.

### Step 6: Process Documents (If Needed)

If you need to reprocess documents:

```bash
cd document_preprocessing
python preprocessing_pipeline.py

cd ../vector_database
python module3_pipeline.py
```

---

## How to Run

### Option 1: Using Startup Script (Recommended)

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

### Option 2: Manual Startup

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run app.py --server.port 8501
```

### Access the Application

| Service | URL |
|---------|-----|
| Frontend (Streamlit) | http://localhost:8501 |
| Backend API | http://localhost:8000 |
| API Documentation | http://localhost:8000/docs |

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /auth/register | Register a new user |
| POST | /auth/login | Login and get JWT tokens |
| POST | /auth/refresh | Refresh access token |

### Query

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /query | Basic RAG query |
| POST | /query/advanced | Advanced RAG with confidence scoring |

### User

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /stats | Get user statistics |
| GET | /health | System health check |

### Request/Response Examples

**Login Request:**
```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Login Response:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "your_username",
  "role": "finance_employee"
}
```

**Query Request:**
```json
{
  "query": "What was the total revenue for 2024?",
  "top_k": 5
}
```

**Query Response:**
```json
{
  "answer": "Based on the financial reports...",
  "sources": [
    {
      "source_id": "fin_001",
      "document_name": "quarterly_financial_report.md",
      "department": "Finance",
      "relevance_score": 0.89
    }
  ],
  "confidence": {
    "overall_confidence": 85.5,
    "retrieval_quality": 90.0,
    "answer_completeness": 82.0,
    "confidence_level": "high"
  }
}
```

---

## Configuration

### LLM Provider Priority

The system automatically selects an LLM provider based on available API keys:

1. HuggingFace (if HUGGINGFACE_API_KEY is set)
2. OpenAI (if OPENAI_API_KEY is set)
3. Local/Simulated (fallback)

### Supported Models

| Provider | Models |
|----------|--------|
| OpenAI | gpt-4, gpt-4-turbo-preview, gpt-3.5-turbo |
| HuggingFace | meta-llama/Meta-Llama-3.1-8B-Instruct, mistralai/Mistral-7B-Instruct-v0.2 |
| Ollama | Any locally installed model (llama2, mistral, etc.) |

### RAG Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| MAX_CONTEXT_CHUNKS | 5 | Maximum chunks for context |
| RELEVANCE_THRESHOLD | 0.3 | Minimum relevance score |
| CHUNK_SIZE | 512 | Tokens per chunk |
| CHUNK_OVERLAP | 50 | Overlap between chunks |

---

## Module Details

### Environment Setup
- Creates project directory structure
- Generates environment configuration templates
- Sets up logging and data directories

### Document Preprocessing
- **Document Parser**: Handles Markdown, CSV, and text files
- **Document Chunker**: Splits documents into 300-512 token chunks with overlap
- **Text Cleaner**: Normalizes and cleans text content
- **Metadata Tagger**: Adds department and access control metadata

### Vector Database
- **Embedding Generator**: Uses sentence-transformers (all-MiniLM-L6-v2)
- **Vector DB Manager**: ChromaDB integration with RBAC filtering
- Persistent storage for embeddings

### Backend
- FastAPI REST API server
- JWT-based authentication
- SQLite database for user management
- RBAC permission enforcement
- Query logging and statistics

### LLM Integration
- **LLM Manager**: Unified interface for multiple providers
- **Advanced RAG Pipeline**: Complete orchestration with re-ranking
- **Confidence Scorer**: Multi-factor confidence assessment
- **Response Formatter**: Structured response generation

### Frontend
- Streamlit web interface
- Dark/Light mode themes
- Chat interface with history
- Role-based suggested questions
- Source document display
- Confidence metrics visualization

---

## Security Considerations

1. **JWT Tokens**: Short-lived access tokens with refresh mechanism
2. **Password Hashing**: bcrypt for secure password storage
3. **RBAC Enforcement**: Applied at both API and data levels
4. **Input Validation**: Pydantic schemas for request validation
5. **CORS Configuration**: Configurable allowed origins

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend not starting | Check if port 8000 is available, verify .env configuration |
| Frontend connection error | Ensure backend is running, check API_BASE_URL in app.py |
| No LLM responses | Verify API keys in .env file, check LLM provider status |
| Empty search results | Run preprocessing pipeline to populate vector database |
| Authentication failures | Clear browser cache, check JWT_SECRET_KEY |

---

