AI-Company-Internal-Chatbot-with-Role-Based-Access-Control-RBAC-
AI Company Internal Chatbot with Role-Based Access Control (RBAC)

This project implements a secure, enterprise-focused internal AI chatbot that enables employees to query company documents using natural language while strictly enforcing Role-Based Access Control (RBAC). The system integrates Retrieval-Augmented Generation (RAG) to ensure responses are accurate, context-aware, and derived only from authorized data sources.

The solution is designed for organizations where data privacy, compliance, and controlled access are critical. Each document is processed, chunked, embedded, and tagged with role-based metadata, ensuring users retrieve only the information permitted by their assigned role.

🔐 Core Objectives

Enable secure natural language access to internal knowledge

Enforce strict department-wise data isolation

Prevent unauthorized document retrieval at the database level

Use open-source and free tools for cost-effective deployment

👥 Supported User Roles

Finance: Financial reports and summaries

HR: Employee data and HR records

Engineering: Technical and architecture documentation

Marketing: Campaign and market analysis reports

C-Level: Organization-wide unrestricted access

General Users: Limited, configurable access

🛠️ Technology Stack

Backend: FastAPI (Python) for API orchestration

Frontend: Streamlit for interactive chatbot interface

Vector Database: ChromaDB for semantic search

Embeddings: SentenceTransformers (all-MiniLM-L6-v2)

Authentication: JWT-based security (PyJWT)

LLM: OpenAI GPT (optional) with fallback mode

⚙️ Key Features

JWT Authentication & Secure Sessions

Metadata-Based RBAC Filtering during vector search

Retrieval-Augmented Generation (RAG) pipeline

Document Chunking to handle context window limits

Source-Cited Responses for transparency and auditing
