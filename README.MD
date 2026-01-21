
# 🤖 FinBot – RAG-Based Chatbot with Role-Based Access Control(RBAC)

**FinBot** is a secure, role-aware AI assistant designed for internal company usage.

It uses Retrieval-Augmented Generation (RAG) to answer employee queries strictly from authorized documents, ensuring data privacy and access control.

The system integrates FastAPI, LangChain, ChromaDB, Ollama (local LLM), and Streamlit into a scalable and secure chatbot platform.

---

## 🚀 Key Features

 🔐 **JWT-based login & authentication**

 👥 **Role-Based Access Control (RBAC)** 

📄 Retrieval-Augmented Generation (RAG) pipeline

🤖 Local LLM via Ollama (phi-3 / mistral)

🧠 Application-level in-memory caching

📚 ChromaDB vector storage

🌐 Streamlit user interface

🔍 Document chunking, embedding & metadata filtering

📌 Source document traceability

---

## ⚙️ Tech Stack

| Component     | Tool/Service                              |
|---------------|-------------------------------------------|
| LLM           | Ollama (Local LLM: phi-3 / mistral)|
| Backend       | FastAPI                                   |
| Frontend      | Streamlit                                 |
| Vector Store  | ChromaDB                                  |
| Embeddings    | Sentence Transformers (MiniLM)            |
| RAG Pipeline  | LangChain                                 |
| Auth System   | JWT (`python-jose`)                       |
| Cache         | Application-Level In-Memory Cache
---

## 👥 Role Definitions & Access

| Role        | Access To Documents              |
|-------------|----------------------------------|
| **Finance**     | Finance + General             |
| **HR**          | HR + General                  |
| **Marketing**   | Marketing + General           |
| **Engineering** | Engineering + General         |
| **C-Level**     | All departments               |
| **Employee**    | General only                  |

🔒 Access is enforced at **document chunk level** using metadata like `role_Finance=True`.

---
##🧠 Caching Strategy (Application-Level):
-----------------------------------------
FinBot implements application-level in-memory caching to improve performance.

Cache Key: (User Role + Query)

Avoids repeated vector search and LLM calls

Improves response speed significantly

Implemented inside the chatbot service layer

⚠️ Cache is reset automatically when the backend restarts.
----
## 🧱 Architecture Overview

[Streamlit UI] --> /login --> [FastAPI Backend] --> [JWT Token Issued]
                                     ↓
                                /chat POST
                                     ↓
                            Role-Based Filter
                                     ↓
                            [ChromaDB + LangChain]
                                     ↓
                            [Ollama Local LLM]
                                     ↓
                          [Response + Source shown]
Documents are:

-Chunked using RecursiveCharacterTextSplitter

-Stored in ChromaDB

-Embedded using MiniLM

-Tagged with metadata (department, roles, access flags)

-Retrieved using LangChain retriever with role-based filtering
----------------------------------------------------------------------------------------------------------------
🛠️ Setup Instructions:

recommended python version:

----Python 3.11.0----------recommended
-----visual studio code-------recommended
-----Operating System---Windows

🐍 1. Create  Virtual Environment
 
📦 Step 1: Open a terminal inside your project directory and run:

    python -m venv venv

⚙️ Step 2: Activate the Virtual Environment

    .\venv\Scripts\Activate.ps1

🧪 2. Install Dependencies

    pip install -r requirements.txt

🔐 3. Configure .env

---.env file in the root directory of the project:

---Paste your JWT_SECRET_key into it like this:

JWT_SECRET_KEY=your_secret_key_here

LLM_PROVIDER=ollama

OLLAMA_MODEL=phi3

📂 4. Ingest Documents into ChromaDB

 # ✅ This will generate the chroma_db folder from your markdown and CSV files

    python -m backend.ingest


▶️ How to Run the Project:
---------------------------

🟢 1. Start Backend (FastAPI)
   
    uvicorn backend.api.main:app --reload

    Visit: http://127.0.0.1:8000

🖥️ 2. Start Frontend (Streamlit)
    
    streamlit run frontend/app.py

  - Visit: http://localhost:8501

API Testing:
http://127.0.0.1:8000/docs
Test:

/login

/chat

JWT authentication flow

----------------------------------------------------------------------------------------------------------------------

💬 Usage Example
-------------------


Username: hr||marketing||finance||employee||ceo||admin||cto||-- (any one!!)

password: Username123

------------------
Ask Question according to the role:

-What is the company’s vision and mission?--(emploee)

-Where is FinSolve headquartered?--(engineering)

-What was the total revenue in Q4 2024?--(finace)

-What was the customer acquisition target for Q4 2024?--(marketing)

-any question from the company for-- (c-Level)

🔒 Security Features:
-----------------------
--JWT token validation

--Role-based document filtering

--No unauthorized document access

--No raw database fields exposed

--Strict context-only answer generation

### 🔑 Login Credentials

Username examples:
- hr
- finance
- marketing
- employee
- admin

Password format:
`<username>123`

Example:
- Username: hr  
- Password: `hr123`


📁 Folder Structure:

    finbot/
    ├── .env
    ├── README.MD
    ├── requirements.txt
    ├── backend/
    │   ├── ingest.py
    │   ├── users.db
    │   ├── api/
    │   │   ├── auth.py
    │   │   ├── chatbot.py
    │   │   ├── main.py
    │   │   ├── models.py
    │   ├── core/
    │   │   ├── config.py
    │   │   ├── vectorstore.py
            |__ __init__.py
            
    │   ├── db/
            |__seed_users.py
    │   │   ├── user_db.py
    ├── data/
    │   ├── engineering/
    │   ├── finance/
    │   ├── general/
    │   ├── hr/
    │   └── marketing/
    └── frontend/
        └── app.py








