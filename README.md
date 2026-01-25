# 🔐 Secure Internal Chatbot with RBAC & RAG

A secure, role-based internal chatbot built using **Retrieval-Augmented Generation (RAG)** that ensures employees can only access information authorized for their role.  
The system combines **FAISS vector search**, **LangChain**, **Ollama LLM**, and a **Streamlit UI** to deliver fast, accurate, and secure responses.

---

## 🚀 Key Features

- 🔐 **Role-Based Access Control (RBAC)**
  - Users can only access documents permitted to their role
  - C-Level users have full organizational access
  - Unauthorized data is never sent to the LLM

- 🤖 **Retrieval-Augmented Generation (RAG)**
  - Documents are embedded and indexed using FAISS
  - Relevant chunks are retrieved before generating responses
  - Prevents hallucinations by grounding answers in data

- 🔍 **Role-Based Query Suggestions UI**
  - Users see suggested questions based on their role
  - Reduces vague queries and improves retrieval accuracy

- ⚡ **Optimized Performance**
  - Cached embeddings, vector store, and LLM
  - Faster responses after first query

- 🖥 **Streamlit Web Interface**
  - Simple login system
  - Clean and user-friendly UI
  - Source document visibility

---

## 🧱 System Architecture

User → Streamlit UI
→ Authentication (SQLite)
→ Role Identification
→ FAISS Vector Search (Role-filtered)
→ LLM (Ollama)
→ Secure Answer


---

## 👥 Supported Roles

| Role        | Access Scope |
|------------|--------------|
| Employee   | Employee handbook & general policies |
| HR         | HR documents and policies |
| Finance    | Financial and quarterly reports |
| Engineering| Engineering guidelines |
| Marketing  | Marketing reports |
| C-Level    | Full access to all documents |

---

## 🔑 Demo Credentials

| Username | Password | Role |
|--------|----------|------|
| admin  | admin123 | C-Level |
| hr     | hr123    | HR |
| fin    | fin123   | Finance |
| eng    | eng123   | Engineering |
| mkt    | mkt123   | Marketing |
| emp    | emp123   | Employee |

---

## 📂 Project Structure

secure-internal-chatbot/
│
├── streamlit_app.py # UI
├── rag_engine.py # RAG + RBAC logic
├── auth.py # Authentication
├── data_ingest.py # FAISS index creation
├── roles.py # Role definitions
├── requirements.txt
├── README.md
│
├── data/ # Source documents
├── faiss_index/ # Vector database
└── screenshots/ # Demo screenshots


---

## ⚙️ Installation & Setup

### 1️⃣ Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate
2️⃣ Install dependencies
pip install -r requirements.txt
3️⃣ Create FAISS index
python data_ingest.py
4️⃣ Run the application
streamlit run streamlit_app.py
