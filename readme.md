# Company Internal Chatbot with Role-Based Access Control (RBAC)

## Internship Project – Infosys Springboard

---

## 📌 Project Overview

This project implements a **secure, enterprise-style internal chatbot system** that enables authenticated users to query internal company knowledge while strictly enforcing **Role-Based Access Control (RBAC)**. The system is designed to reflect real-world organizational security and compliance standards by ensuring that sensitive information is accessible only to authorized roles and departments.

The architecture follows a **Retrieval-Augmented Generation (RAG)** design pattern. Company documents are optionally embedded and indexed into a **Vector Database (ChromaDB)** using a semantic ingestion pipeline. During runtime, the system applies multi-layer role validation and generates **AI-powered summaries** using a **Local Large Language Model (LLM)**.

To ensure stability during live demonstrations, the system supports a **fallback retrieval mode** that enforces RBAC without dependency on the vector database while maintaining full AI summarization capabilities.

---

## 🎯 Project Objectives

- Design and implement **secure authentication** using JWT-based token management  
- Enforce **role-based authorization** across all backend endpoints  
- Restrict document access using **department-level RBAC policies**  
- Integrate **AI-driven summarization** using a local LLM engine  
- Implement **Retrieval-Augmented Generation (RAG)** with semantic vector search  
- Maintain **source attribution** for transparency and explainability  
- Demonstrate **enterprise-grade backend and security architecture**

---

## 🧠 System Architecture

```
User
 ↓
Streamlit Frontend (Web Interface)
 ↓
FastAPI Backend (REST API Layer)
 ↓
JWT Authentication & Token Validation
 ↓
RBAC Enforcement Engine
 ↓
Document Retrieval Layer
   ├── Fallback Mode (Folder + Keyword Matching)
   └── RAG Mode (ChromaDB + Semantic Search)
 ↓
Local LLM (Ollama – AI Summarization)
 ↓
Response + Source Attribution
```

---

## 🔐 Security Model

### Authentication
- Users authenticate using a **username and password**
- The system issues:
  - **Access Tokens (Short-lived JWT)**
  - **Refresh Tokens (Long-lived JWT)**

### Authorization
- All protected API routes require a **Bearer Token**
- Tokens are decoded and validated server-side
- User roles are verified before document retrieval is permitted

### Access Control Strategy
The system enforces **Multi-Layer RBAC**:
1. API-level token validation  
2. Role verification against enterprise role policies  
3. Folder-level department isolation  
4. Query-based intent filtering and enforcement  

---

## 👥 Roles and Permissions

| Role | Authorized Access Scope |
|------|--------------------------|
| intern | General company handbook and non-sensitive documents |
| finance | Financial reports, quarterly summaries, and revenue documents |
| hr | Employee records and HR datasets |
| marketing | Campaign analysis and marketing reports |
| engineering | Technical and engineering documentation |
| admin (C-Level) | Full system-wide access |

---

## 📁 Project Structure

```
company-rbac-chatbot/
│
├── backend/
│   ├── main.py
│   ├── auth.py
│   ├── rbac.py
│   ├── rag.py
│   └── ingest.py
│
├── data/
│   └── raw_docs/
│       ├── Finance/
│       ├── HR/
│       ├── marketing/
│       ├── engineering/
│       └── general/
│
├── frontend/
│   └── app.py
│
├── chroma_db/
├── users.db
└── venv/
```

---

## ⚙️ Technology Stack

- Backend: FastAPI  
- Frontend: Streamlit  
- Authentication: JWT (JSON Web Tokens)  
- Database: SQLite  
- Vector Database: ChromaDB  
- AI Engine: Ollama (Local LLM)  
- Embedding Model: Sentence Transformers (MiniLM)  
- Language: Python  
- API Protocol: REST  

---

## 🔁 Functional Workflow

1. User registers with a valid enterprise role  
2. User logs in and receives JWT tokens  
3. User submits a query via the web interface  
4. Backend validates token and extracts role  
5. RBAC engine verifies document permissions  
6. Authorized documents are retrieved  
7. AI engine summarizes the content  
8. Response is returned with source attribution  

---

## 🤖 Semantic Ingestion Pipeline (ChromaDB)

The system includes a semantic ingestion module that prepares documents for Retrieval-Augmented Generation.

### Ingestion Capabilities
- Department-level document scanning  
- Text extraction from Markdown, CSV, and TXT formats  
- Embedding generation using Sentence Transformers  
- Vector storage in ChromaDB  
- Metadata tagging for role-based filtering  

---

## 🧪 API Endpoints

### Authentication
- POST /auth/register  
- POST /auth/login  
- POST /auth/refresh  

### Knowledge Retrieval
- GET /search  
  - Requires Bearer token  
  - Enforces RBAC  
  - Returns AI summary and document sources  

---

## 🎥 Demonstration Flow

1. Register users with different roles  
2. Login as Intern → Query finance data → Access Denied  
3. Login as Finance → Query finance data → Summary Returned  
4. Login as Admin → Query HR or Engineering → Full Access  

---

## 🏗️ Design Principles

- Zero Trust Security Model  
- Separation of Concerns  
- Defense-in-Depth Architecture  
- Scalable API Design  
- Enterprise RBAC Standards  
- Explainable AI through Source Attribution  

---

## 📈 Learning Outcomes

- Implemented JWT-based authentication systems  
- Designed enterprise RBAC architecture  
- Built semantic ingestion pipelines using vector databases  
- Integrated local AI models for document summarization  
- Developed secure REST APIs  
- Applied real-world software security patterns  

---

## 🔮 Future Enhancements

- Cloud Deployment (Azure / AWS)  
- Role Management Dashboard  
- Audit Logging and Monitoring  
- Multi-Factor Authentication (MFA)  
- Advanced Semantic Ranking  
- Distributed Vector Database Support  

---

## 👩‍💻 Author

Narayana Sathvika  
B.Tech – Artificial Intelligence & Machine Learning  
Infosys Springboard Intern  

---

## 📄 License

This project is developed for academic and internship evaluation purposes. Commercial use is restricted.
