Company Internal Chatbot with Role-Based Access Control (RBAC)

# 🔐 Internal Chatbot with Role-Based Access Control (RBAC)

## 📌 Project Title

**Internal Company Knowledge Chatbot with Role-Based Access Control (RBAC)**

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

### 🧠 Semantic Search (RAG)

* SentenceTransformer embeddings (`all-MiniLM-L6-v2`)
* ChromaDB persistent vector store
* Query normalization and rewriting
* Query variant generation
* Re-ranking using hybrid semantic scoring
* Deduplication across documents

### 📚 Transparent Citations

* Answers generated only from authorized chunks
* Source documents shown per answer
* Chunk-level relevance indicators
* Secure dataset download (RBAC enforced)

### ⚡ Performance Optimizations

* In-memory UI query cache (per role)
* Cache invalidation support
* Efficient chunk overlap strategy

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

### Frontend

* **Streamlit** – UI framework
* **Requests** – API communication

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
│   ├── auth/                # Authentication & RBAC
│   ├── semantic_search/     # Secure semantic retrieval
│   ├── RBAC/                # RBAC configuration
│   ├── chunking/            # Chunk generation
│   ├── cleaning/            # Dataset cleaning
│   ├── Embeddings/          # Embedding generation
│   ├── chroma_db/           # Persistent vector store
│   └── admin.py             # Audit APIs
│
├── frontend/
│   ├── app.py               # Main Streamlit app
│   ├── auth_ui.py           # Login UI
│   ├── rag_ui.py            # Chat interface
│   └── admin_audit_ui.py    # Audit UI
│
├── normalized_datasets/     # Cleaned datasets
├── tests/                   # Verification tests
├── data/auth.db             # SQLite auth DB
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions (Verified)

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

Backend runs at:

```
http://127.0.0.1:8000
```

---

### 7️⃣ Run Frontend UI

```bash
streamlit run frontend/app.py
```

Frontend runs at:

```
http://localhost:8501
```

---

## 🧪 Testing & Validation

The `tests/` folder includes:

* JWT validation tests
* RBAC authorization tests
* RAG pipeline tests
* End-to-end verification

Example:

```bash
python tests/verify_phase2_full.py
```

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

