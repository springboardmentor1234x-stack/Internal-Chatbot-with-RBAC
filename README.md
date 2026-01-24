Enterprise Internal AI Knowledge Assistant
Overview

The Enterprise Internal AI Knowledge Assistant is a secure, role-based, Retrieval-Augmented Generation (RAG) system designed for internal organizational use.
It enables employees to query company knowledge safely and accurately while enforcing strict Role-Based Access Control (RBAC) and preventing hallucinations.
The system uses local Large Language Models (LLMs) and a vector database to ensure that answers are generated only from authorized internal documents.

Key Objectives

Provide accurate, document-grounded answers to internal queries
Enforce department-level access restrictions
Prevent hallucinations and cross-department data leakage
Support enterprise-grade auditing and traceability
Deliver a clean, professional UI for demonstrations and real usage

Core Features
1. Retrieval-Augmented Generation (RAG)

Documents are chunked, embedded, and stored in a vector database
Queries retrieve only the most relevant document chunks
LLM responses are strictly grounded in retrieved context

2. Role-Based Access Control (RBAC)

Users are assigned roles (Marketing, Finance, HR, Engineering, C-Level)
Each document chunk is tagged with allowed roles
Retrieval is filtered at the vector database level

3. Local LLM Execution

Uses a local model (Flan-T5)
No external API dependency
Ensures data privacy and compliance

4. Intent Classification

Separates conversational queries from knowledge queries
Prevents unnecessary document retrieval
Improves user experience and system safety

5. Document Traceability

Every response includes clickable source documents
Users can view the original content used to generate answers

System Architecture

User (Streamlit UI)
        |
        v
FastAPI Backend
        |
        ├── Authentication (JWT)
        ├── Intent Classification
        ├── Role Validation
        |
        v
RAG Pipeline
        |
        ├── Vector Retrieval (ChromaDB)
        ├── Role-Filtered Results
        ├── Re-ranking
        |
        v
Local LLM (Flan-T5)
        |
        v
Grounded Answer + Sources

Technology Stack

Backend
FastAPI
JWT Authentication
SQLite (User DB)
SentenceTransformers
ChromaDB (Persistent Vector Store)
Local LLM (Flan-T5)

Frontend
Streamlit
Custom HTML/CSS styling
Role-aware UI components

Project Structure

ai-company-chatbot/
│
├── backend/
│   ├── api/
│   │   ├── auth_api.py
│   │   ├── register_api.py
│   │   └── chat_api.py
│   │
│   ├── auth/
│   │   ├── jwt_handler.py
│   │   ├── password_utils.py
│   │   └── audit.py
│   │
│   ├── rag/
│   │   ├── chunker.py
│   │   ├── retriever.py
│   │   ├── llm.py
│   │   ├── intent.py
│   │   └── rag_pipeline_llm.py
│   │
│   ├── db/
│   │   └── database.py
│   │
│   ├── models/
│   │   └── user_model.py
│   │
│   └── main.py
│
├── data_ingestion/
│   └── scripts/
│       ├── ingest.py
│       ├── embed_store.py
│       ├── parser.py
│       ├── preprocess.py
│       └── metadata.py
│
├── Fintech-data/
│   ├── marketing/
│   ├── finance/
│   ├── hr/
│   ├── engineering/
│   └── general/
│
├── frontend/
│   └── app.py
│
├── vector_db/
│   └── chroma_store/
│
├── users.db
├── requirements.txt
└── README.md

Data Ingestion Pipeline
Steps
Load documents from Fintech-data/
Clean and normalize text
Chunk documents into semantic units
Attach metadata (department, roles, source)
Generate embeddings
Store in ChromaDB

Run Ingestion
python -m data_ingestion.scripts.ingest

Authentication & Authorization
Users register with a role
JWT tokens are issued on login
Each API request is authenticated
Role is extracted from token and enforced at retrieval time

Chat Workflow
User sends query
Token is validated
Intent is classified
If conversational → direct LLM response
If knowledge-based:
Retrieve role-authorized chunks
Build grounded context
Generate answer from LLM
Return answer with document sources

Running the Application
1. Create Virtual Environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

2. Install Dependencies
pip install -r requirements.txt

3. Run Backend
uvicorn backend.main:app --reload

4. Run Frontend
streamlit run frontend/app.py

Example Test Queries
Greeting
hello

Role Check
what is my role

Authorized Query
summarize marketing performance for last quarter

Unauthorized Query
show finance revenue


Security Considerations

No external LLM API calls
Strict role filtering before generation
No response without retrieved context
Full audit logging capability

Future Enhancements

PDF viewer with highlighted citations
Admin analytics dashboard
Feedback-driven re-ranking
Streaming responses
Multi-tenant support

Conclusion

This project demonstrates a production-grade internal AI assistant with strong emphasis on security, accuracy, and enterprise usability.
It is suitable for academic evaluation, interviews, internships, and real-world enterprise deployment scenarios.
