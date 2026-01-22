Features
Core Functionality

AI-Powered Question Answering: Ask natural language questions on internal company documents.

Retrieval-Augmented Generation (RAG): Responses are generated using retrieved document context.

Vector Similarity Search: Semantic document retrieval using ChromaDB embeddings.

Source Transparency: Every answer includes document sources with download support.

Security & Access Control

JWT Authentication: Secure token-based user authentication.

Role-Based Access Control (RBAC): Department-specific access to documents.

Backend-Enforced Security: Roles are validated on the backend, not the UI.

Secure Password Hashing: Passwords are hashed using Argon2.

User Experience

Interactive Streamlit UI: Simple and intuitive chat-based interface.

Role-Aware Responses: Users only see information permitted by their role.

Error Handling: Graceful handling of unauthorized access and expired sessions.

📋 System Architecture
Backend (FastAPI)
User Query
    ↓
JWT Authentication
    ↓
RBAC Validation
    ↓
Vector Search (ChromaDB)
    ↓
Context Retrieval
    ↓
LLM Generation (Flan-T5)
    ↓
Answer + Sources

Frontend (Streamlit)
Login Interface
    ↓
Chat Interface
    ↓
Response Display
    ↓
Source Download

🧠 RAG Pipeline Flow

User submits a natural language query.

Query is converted into vector embeddings.

Relevant document chunks are retrieved from ChromaDB.

RBAC filtering ensures only authorized documents are used.

Retrieved context is passed to the LLM.

Final response is generated with document sources.

👥 User Roles & Permissions
Role	Access Scope
Finance	Finance + General documents
HR	HR + General documents
Marketing	Marketing + General documents
Engineering	Engineering + General documents
General (Employee)	General documents only

Access control is strictly enforced in the backend using JWT role claims.

🛠️ Technology Stack
Layer	Technology
Frontend	Streamlit
Backend	FastAPI
Authentication	JWT + Argon2
Vector Database	ChromaDB
Embeddings	Sentence Transformers
LLM	Google Flan-T5
Database	SQLite
Language	Python
🛠️ Setup Instructions
Prerequisites

Python 3.10+

SQLite

Virtual environment (recommended)

Installation

Clone the repository:

git clone <your-repository-url>
cd rbac-rag-internal-chatbot


Create virtual environment and install dependencies:

pip install -r requirements.txt

Environment Variables

Create a .env file inside the backend/ folder:

JWT_SECRET=your_secret_key_here

🚀 Running the Application
Start Backend
cd backend
uvicorn main:app --reload


Backend runs at:

http://127.0.0.1:8000


Swagger Docs:

http://127.0.0.1:8000/docs

Start Frontend
cd frontend
streamlit run app.py


Frontend runs at:

http://localhost:8501

📁 Project Structure
rbac-rag-internal-chatbot/
│
├── backend/
│   ├── main.py
│   ├── users.db
│   ├── .env.example
│
├── frontend/
│   ├── app.py
│
├── Fintech-data/
│   ├── finance/
│   ├── hr/
│   ├── marketing/
│   ├── engineering/
│   ├── general/
│
├── README.md
└── .gitignore

🔐 Security Highlights

Passwords hashed using Argon2

JWT-based stateless authentication

RBAC enforced at backend

No secrets hardcoded in code

Frontend never passes role information

🔮 Future Enhancements

Admin interface for role management

Query history and analytics

Fine-grained document-level access control

Feedback-based answer improvement

📊 Measurable Impact

Reduced time to retrieve internal information

Improved data security and access control

Increased trust through source-backed responses