import os
from typing import List
from operator import itemgetter
from dotenv import load_dotenv

# LangChain Imports
from langchain_community.document_loaders import UnstructuredMarkdownLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
DATA_PATH = "./rag_data"
CHROMA_PATH = "./data/chroma"
EMBEDDING_MODEL = "text-embedding-ada-002"
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.1

# Document-to-Role Mapping
DOCUMENT_MAP = {
    "quarterly_financial_report.md": ["Finance", "C-Level"],
    "marketing_report_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q1_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q2_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q3_2024.md": ["Marketing", "C-Level"],
    "market_report_q4_2024.md": ["Marketing", "C-Level"],
    "hr_data.csv": ["HR", "C-Level"],
    "employee_handbook.md": [
        "HR",
        "Employee",
        "C-Level",
        "Finance",
        "Marketing",
        "Engineering",
    ],
    "engineering_master_doc.md": ["Engineering", "C-Level"],
}

# --- 1. SETUP FUNCTIONS ---


def load_documents() -> List:
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data directory not found at {DATA_PATH}.")
        return []

    all_documents = []
    for filename, roles in DOCUMENT_MAP.items():
        file_path = os.path.join(DATA_PATH, filename)
        if not os.path.exists(file_path):
            continue

        loader = (
            CSVLoader(file_path, encoding="utf-8")
            if filename.endswith(".csv")
            else UnstructuredMarkdownLoader(file_path)
        )
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )
        chunks = text_splitter.split_documents(docs)

        for chunk in chunks:
            chunk.metadata["allowed_roles"] = roles
            chunk.metadata["source"] = filename
            all_documents.append(chunk)

    return all_documents


def create_vector_store():
    documents = load_documents()
    if not documents:
        return

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    if os.path.exists(CHROMA_PATH):
        import shutil

        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(documents, embeddings, persist_directory=CHROMA_PATH)
    db.persist()
    print("Vector store created.")


# --- 2. RETRIEVAL & CHAIN LOGIC ---


def get_rag_chain(user_role: str):
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

    # RBAC Filter: ensures the user can only see docs matching their role
    chroma_filter = {"allowed_roles": {"$in": [user_role]}}

    retriever = db.as_retriever(search_kwargs={"k": 5, "filter": chroma_filter})
    llm = ChatOpenAI(temperature=LLM_TEMPERATURE, model=LLM_MODEL)

    template = """
    You are an internal chatbot for FinSolve Technologies. Use the following context to answer the question. 
    Your current role is {user_role}. Cite sources as [Source: filename].
    If the answer isn't in the context, say: "Information not available in authorized documents."

    Context: {context}
    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    def format_docs(docs):
        return "\n\n".join(
            [
                f"Source: {d.metadata.get('source')}\nContent: {d.page_content}"
                for d in docs
            ]
        )

    chain = (
        {
            "context": itemgetter("question") | retriever | format_docs,
            "question": itemgetter("question"),
            "user_role": itemgetter("user_role"),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


# --- 3. API WRAPPER FUNCTION ---


def run_rag_query(question: str, role: str):
    """The main entry point for the FastAPI backend."""
    if not os.path.exists(CHROMA_PATH):
        return "System error: Vector database not found. Please run setup first."

    try:
        chain = get_rag_chain(role)
        return chain.invoke({"question": question, "user_role": role})
    except Exception as e:
        return f"Error processing query: {str(e)}"


if __name__ == "__main__":
    create_vector_store()
