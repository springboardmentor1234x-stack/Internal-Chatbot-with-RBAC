# 🔐 Internal Chatbot with Role-Based Access Control (RBAC)

## 📌 Project Title

**Company Internal Chatbot with Role-Based Access Control (RBAC)**

---

## 📖 Description

This project is a **secure internal knowledge chatbot** designed for organizations to query internal documents using **semantic search**, while strictly enforcing **Role-Based Access Control (RBAC)**.

Unlike generic chatbots, this system ensures that:

* Users **only see content they are authorized to access**
* Authorization is enforced **before retrieval, during retrieval, and at response time**
* Every answer is grounded in **verifiable internal documents**, with transparent citations

The application combines:

* Data cleaning and preprocessing
* Intelligent document chunking
* Vector embeddings and similarity search
* Secure RBAC enforcement
* A user-friendly Streamlit-based chat UI

---

## ✨ Key Features

### 🔐 Security & RBAC

* JWT-based authentication
* Hierarchical role inheritance
* Permission-based access control
* Department-level document isolation
* Token expiry & blacklist handling
* Audit log tracking for admin users

---

### 🧠 Semantic Search (RAG)

* SentenceTransformer embeddings (`all-MiniLM-L6-v2`)
* ChromaDB persistent vector store
* Query normalization and rewriting
* Query variant generation
* Re-ranking using hybrid semantic scoring
* Deduplication across documents

---

### 📚 Transparent Citations

* Answers generated only from authorized chunks
* Source documents shown per answer
* Chunk-level relevance indicators
* Secure dataset download (RBAC enforced)

---

### ⚡ Performance Optimizations

* In-memory UI query cache (per role)
* Cache invalidation support
* Efficient chunk overlap strategy

---

### 🖥️ User Experience

* Streamlit-based chat interface
* Role-aware UI rendering
* Admin-only audit log view
* Session expiry handling

---

## 🏗️ Architecture Overview

```
Raw Datasets
     ↓
[ Cleaning Pipeline ]
     ↓
[ Normalized Text Files ]
     ↓
[ Chunking + Metadata Generation ]
     ↓
[ Embedding Generation ]
     ↓
[ ChromaDB Vector Store ]
     ↓
[ RBAC Filter → Semantic Search ]
     ↓
[ LLM Answer Generation ]
     ↓
[ Streamlit Chat UI + Citations ]
```

---

### 🔒 RBAC Flow (Critical Design)

1. User authenticates and receives JWT
2. User role is resolved and normalized
3. Permissions are expanded via role inheritance
4. Allowed departments are derived
5. **Only authorized chunks are retrieved from ChromaDB**
6. Semantic ranking is applied **after authorization**

---

## 🧰 Tech Stack

### Backend

* **Python**
* **FastAPI** – REST API
* **SQLAlchemy** – ORM
* **SQLite** – Authentication & audit DB
* **JWT (PyJWT)** – Authentication
* **Passlib (bcrypt)** – Password hashing
* **ChromaDB** – Vector database
* **SentenceTransformers** – Embeddings

---

### Frontend

* **Streamlit** – UI framework
* **Requests** – API communication

---

### Data & ML

* **NumPy** – Embeddings storage
* **JSON** – Metadata & RBAC config

---

## 👥 User Roles Supported

Examples of roles supported (via RBAC configuration):

* intern
* employee
* engineering_employee
* engineering_manager
* finance_employee
* finance_manager
* hr_employee
* hr_manager
* marketing_employee
* marketing_manager
* admin (Audit access)
* c_level

Roles can inherit permissions from parent roles (defined in `rbac.json`).

---

## 📁 Project Structure

```
Internal-Chatbot-with-RBAC/
├── backend/
│   ├── auth/                      # Authentication, JWT, RBAC utilities
│   │   ├── auth_utils.py
│   │   ├── dependencies.py
│   │   ├── jwt_handler.py
│   │   ├── permissions.py
│   │   ├── rbac.py
│   │   ├── role_permissions.py
│   │   └── token_blacklist.py
│   │
│   ├── rag/                       # RAG orchestration & enforcement
│   │   ├── action_rbac.py
│   │   ├── llm.py
│   │   ├── orchestrator.py
│   │   ├── retrieval.py
│   │   └── role_normaliser.py
│   │
│   ├── RBAC/                      # RBAC configuration
│   │   └── rbac.json
│   │
│   ├── semantic_search/           # Secure semantic search APIs
│   │   ├── admin.py
│   │   └── api.py
│   │
│   └── chroma_db/                 # Persistent Chroma vector store
│
├── chunking/                      # Document chunk generation
│   ├── chunk.py
│   ├── student_chunks.json
│   └── student_metadata.json
│
├── cleaning/                      # Dataset cleaning pipeline
│   └── cleaned.py
│
├── Embeddings/                    # Embedding generation & indexes
│   ├── embeddings.py
│   ├── chunk_embeddings.npy
│   └── embedding_index.json
│
├── data/
│   ├── database/
│   │   ├── models/               # SQLAlchemy models
│   │   │   ├── audit_log.py      # Audit log database model
│   │   │   ├── role.py
│   │   │   └── user.py
│   │   ├── audit.py              # Central audit logging service
│   │   ├── check_db.py
│   │   ├── crud.py
│   │   ├── db.py
│   │   ├── init_db.py
│   │   └── seed.py
│   │
│   └── auth.db                   # SQLite authentication & audit database
│
├── frontend/
│   ├── assets/
│   │   └── styles.css
│   ├── app.py                    # Main Streamlit application
│   ├── auth_ui.py                # Login UI
│   ├── rag_ui.py                 # Chat interface
│   └── admin_audit_ui.py         # Admin audit UI
│
├── normalized_datasets/          # Cleaned, department-wise datasets
│   ├── engineering/
│   ├── finance/
│   ├── general/
│   ├── hr/
│   └── marketing/
│
├── .env                          # Environment variables (ignored by Git)
├── .gitignore
├── requirements.txt
├── README.md
├── check_tables.py
└── Dataset Mapping Table (Task) (2).xlsx

```

---

## ⚙️ Setup Instructions 

### 1️⃣ Clone the Repository

```bash
git clone <repository-url>
cd Internal-Chatbot-with-RBAC
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Initialize Authentication Database

```bash
python init_db.py
```

This creates user, role, and audit tables in `auth.db`.

---

### 5️⃣ Data Preparation Pipeline

#### a) Clean Raw Datasets

```bash
python backend/cleaning/cleaned.py
```

#### b) Generate Chunks & Metadata

```bash
python backend/chunking/chunk.py
```

#### c) Generate Embeddings

```bash
python backend/Embeddings/embeddings.py
```

#### d) Load into ChromaDB

```bash
python backend/semantic_search/load_into_chroma.py
```

---

### 6️⃣ Run Backend API

```bash
uvicorn backend.api:app --reload
```

**Backend URL**

```
http://127.0.0.1:8000
```

---

### 7️⃣ Run Frontend UI

```bash
streamlit run frontend/app.py
```

**Frontend URL**

```
http://localhost:8501
```

---

## 🔍 API Endpoints

### 🔑 Authentication

| Method | Endpoint      | Description              |
| ------ | ------------- | ------------------------ |
| POST   | /auth/login   | Login                    |
| POST   | /auth/logout  | Logout + token blacklist |
| POST   | /auth/refresh | Refresh access token     |
| GET    | /user/profile | User profile             |

---

### 🔎 Search & RAG

| Method | Endpoint | Description                   |
| ------ | -------- | ----------------------------- |
| POST   | /search  | RBAC-enforced semantic search |
| POST   | /ask     | RAG-based question answering  |

---

### 📂 Secure Dataset Download

| Method | Endpoint                                               |
| ------ | ------------------------------------------------------ |
| GET    | /downloads/normalized_datasets/{department}/{filename} |

✔ RBAC enforced
✔ Path traversal protection

---

### 📜 Admin Audit

| Method | Endpoint          |
| ------ | ----------------- |
| GET    | /admin/audit/logs |

🔒 Admin permission required

---

## 🧠 RAG Pipeline (Execution Flow)

* Normalize user role
* Enforce action-level RBAC
* Retrieve only authorized chunks
* Summarize retrieved chunks
* Generate final answer
* Hard block if no authorized content
* Audit log all outcomes

✔ No hallucinations
✔ No cross-role leakage

---

.

📜 Audit Logging & Admin Monitoring

The system implements persistent, centralized backend audit logging to ensure security, traceability, and compliance across all sensitive operations. Audit logging is enforced at the backend level and is fail-safe, meaning audit failures never interrupt core application workflows.

🗄️ Audit Storage

Database: SQLite (auth.db)

Table: audit_logs

Model: data/database/models/audit_log.py

Timestamp Standard: UTC

Each audit record is append-only and immutable once written.

🧾 Audit Record Contents

Each audit entry captures the following information:

Username

Role at the time of action

User ID (if available)

Action performed

Query text (for search or RAG requests, if applicable)

List of accessed documents (stored safely as JSON)

Timestamp

🔍 Audited System Events

The following system events are automatically logged:

LOGIN

LOGOUT

SEARCH

RAG_QUERY_SUCCESS

RAG_RBAC_DENIED

RBAC_ALLOWED

RBAC_DENIED

DOWNLOAD_DATASET

TOKEN_EXPIRED

INVALID_TOKEN

🧠 Audit Design Principles

Centralized audit entry point via a dedicated logging function

Fail-safe logging (audit failures never affect user operations)

JSON-safe storage for document metadata

No debug or console logs exposed to end users

RBAC-aware logging, preserving role context at the time of action

🛡️ Admin Audit Interface

Audit logs are read-only

Accessible only to Admin users

Exposed via a dedicated Streamlit Admin Audit UI

Supports filtering by:

Username

Action type

This interface is designed for compliance review, operational monitoring, and security analysis, while fully preserving RBAC guarantees and data isolation.

## 🚀 Deployment Strategy

This project is currently deployed in a **Local Development Environment** and is architected to seamlessly transition to **Production Deployment** with minimal configuration changes.

The deployment strategy follows **industry best practices** for security, configuration management, and scalability.

---

### 🖥️ Local Development Deployment (Current Mode)

The application is presently configured for local development, where both backend and frontend services are executed on the developer’s local machine.

#### ✔ Deployment Characteristics

* Backend Framework: FastAPI served via Uvicorn
* Frontend Framework: Streamlit
* Database: SQLite (local file-based database)
* Configuration Management: Environment variables loaded from `.env`
* Secrets Handling: No hardcoded secrets in source code
* Version Control Safety: Sensitive files excluded using `.gitignore`

---

### 📦 Local Deployment Setup Steps

#### Step 1: Dependency Freezing

```bash
pip freeze > requirements.txt
```

✔ Already completed for this project.

---

#### Step 2: Environment Variable Configuration

```
GROQ_API_KEY=your_groq_api_key
JWT_SECRET_KEY=your_jwt_secret_key
DATABASE_URL=sqlite:///data/auth.db
BACKEND_URL=http://127.0.0.1:8000
```

⚠️ **Security Note:**
The `.env` file is intentionally excluded from version control using `.gitignore`.

---

#### Step 3: Database Initialization

```bash
python data/database/init_db.py
```

---

#### Step 4: Backend API Startup

```bash
uvicorn backend.api:app --reload
```

**Swagger Docs**

```
http://127.0.0.1:8000/docs
```

---

#### Step 5: Frontend UI Startup

```bash
streamlit run frontend/app.py
```

---

## 🌐 Production Deployment (Future-Ready Design)

Although currently deployed locally, the system is production-ready by design.

### 🔧 Required Production Changes

* Replace SQLite with PostgreSQL / MySQL
* Supply environment variables using:

  * Docker secrets
  * Cloud provider secret managers
  * CI/CD pipelines
* Disable `--reload` in Uvicorn
* Run the backend behind a reverse proxy (e.g., Nginx)

---

### ✅ Production-Grade Features Already Implemented

* No hardcoded credentials or secrets
* Environment-based configuration
* RBAC enforcement at:

  * API level
  * Retrieval level
  * Response generation level
* Secure JWT lifecycle management
* Comprehensive audit logging
* Stateless backend architecture

---

### ✅ Deployment Summary

| Component             | Status                           |
| --------------------- | -------------------------------- |
| Deployment Type       | Local Development                |
| Environment Variables | ✅ Externalized                   |
| Secrets Management    | ✅ `.env + .gitignore`            |
| Database              | SQLite (Local)                   |
| Backend               | FastAPI                          |
| Frontend              | Streamlit                        |
| Production Readiness  | ✅ Yes (Infrastructure dependent) |

---

## 🔐 Security & Version Control Compliance

Sensitive configuration files and runtime artifacts are intentionally excluded from version control to maintain security and reproducibility across environments.

---

## 🔍 Design Principles Followed

* **Security-first architecture**
* **RBAC before retrieval** (no post-filtering)
* **Explainable AI outputs (citations)**
* **Separation of concerns**
* **Fail-safe defaults**
* **Production-ready folder structure**

---

## 🚀 Future Enhancements

* Multi-tenant support
* Role-based UI personalization
* Document versioning
* Admin dashboard analytics
* LLM model switching support

---

## ✅ Conclusion

This project demonstrates a **real-world, enterprise-grade internal chatbot** with:

* Strong security guarantees
* Robust semantic search
* Transparent and explainable answers
* Clean, extensible architecture

It is suitable for **corporate knowledge management**, **internal policy Q&A**, and **secure AI assistants**.

---

🔒 *Built with security, scalability, and clarity at its core.*
