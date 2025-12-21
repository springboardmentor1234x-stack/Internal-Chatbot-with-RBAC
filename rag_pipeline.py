import os
import pandas as pd
from typing import List

# LangChain Imports
from langchain_community.document_loaders import UnstructuredMarkdownLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from operator import itemgetter
from dotenv import load_dotenv

# Load environment variables (for OPENAI_API_KEY)
load_dotenv()

# --- CONFIGURATION ---
DATA_PATH = "./data/docs"
CHROMA_PATH = "./data/chroma"
EMBEDDING_MODEL = "text-embedding-ada-002"
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.1

# Document-to-Role Mapping for RBAC Tagging
# C-Level has access to all documents by default, so they do not need an explicit tag for every file.
DOCUMENT_MAP = {
    "quarterly_financial_report.md": ["Finance", "C-Level"],
    "marketing_report_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q1_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q2_2024.md": ["Marketing", "C-Level"],
    "marketing_report_q3_2024.md": ["Marketing", "C-Level"],
    "market_report_q4_2024.md": ["Marketing", "C-Level"],
    "hr_data.csv": ["HR", "C-Level"],
    "employee_handbook.md": ["HR", "Employee", "C-Level", "Engineering"], # Common access documents
    "engineering_master_doc.md": ["Engineering", "C-Level"],
    # Note: AI_Company Internal Chatbot with Role-Based Access Control.pdf is excluded
    # as it's a project document, not source data.
}

# --- 1. RAG DATABASE SETUP (Executed ONCE) ---

def load_documents() -> List:
    """Loads all documents from the data directory and assigns RBAC metadata."""
    
    # Ensure data directory exists
    if not os.path.exists(DATA_PATH):
        print(f"Error: Data directory not found at {DATA_PATH}. Please create it and place your documents inside.")
        return []

    all_documents = []
    
    for filename, roles in DOCUMENT_MAP.items():
        file_path = os.path.join(DATA_PATH, filename)
        if not os.path.exists(file_path):
            print(f"Warning: File {filename} not found. Skipping.")
            continue

        if filename.endswith(".csv"):
            # Custom logic for CSV (assuming we want to combine rows into one document)
            loader = CSVLoader(file_path, csv_args={"encoding": "utf-8", "delimiter": ","})
        else:
            # Markdown loader
            loader = UnstructuredMarkdownLoader(file_path)

        # Load documents and attach the base RBAC metadata
        docs = loader.load()
        for doc in docs:
            # Add the metadata for the Chroma filter
            doc.metadata["allowed_roles"] = roles
            doc.metadata["source"] = filename # Keep track of original file
            all_documents.append(doc)
            
    print(f"Loaded {len(all_documents)} raw documents (before splitting).")
    return all_documents


def create_vector_store():
    """
    Loads, splits, embeds, and saves the documents to a local Chroma vector store.
    
    This function should be run *only once* to initialize the database.
    """
    
    # 1. Load documents with RBAC metadata
    documents = load_documents()

    if not documents:
        print("No documents were loaded. Cannot create vector store.")
        return

    # 2. Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # 3. Create Embeddings
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    # 4. Create and Save Chroma Store
    print(f"Creating and saving vector store to {CHROMA_PATH}...")
    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=CHROMA_PATH,
    )
    db.persist()
    print("Vector store successfully created and saved.")


# --- 2. RAG PIPELINE (Executed on every chat query via FastAPI) ---

def get_rag_chain(user_role: str):
    """
    Loads the vector store and creates the RAG chain with the
    role-based metadata filter enforced at the retrieval step.
    """
    
    # 1. Load Vector Store
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    try:
        db = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings
        )
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return None # Return None if DB fails to load

    # 2. Define the RBAC Metadata Filter
    # The filter ensures that the 'allowed_roles' metadata field contains the user's role.
    # Note: 'C-Level' is not explicitly filtered here; they are tagged in the documents.
    chroma_filter = {
        "allowed_roles": {
            "$in": [user_role]
        }
    }
    
    # 3. Create Retriever
    retriever = db.as_retriever(
        search_kwargs={"k": 5, "filter": chroma_filter}
    )

    # 4. Define LLM and Prompt
    llm = ChatOpenAI(temperature=LLM_TEMPERATURE, model=LLM_MODEL)
    
    # Note: Using a simplified prompt for clarity
    template = """
    You are an internal corporate chatbot. Use the following context to answer the user's question. 
    You MUST cite your source(s) at the end of the answer by referencing the document name (e.g., [Source: employee_handbook.md]).
    
    If the context does not contain the answer, you MUST state, "I cannot answer this question because the information is not available in your authorized documents."
    
    Your role is: {user_role}. Only use authorized documents provided in the context.

    Context:
    ---
    {context}
    ---
    
    Question: {question}
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # 5. Build the RAG Chain using LangChain Expression Language (LCEL)
    def format_docs(docs):
        # Format documents for the prompt
        return "\n\n".join([f"Source: {d.metadata.get('source', 'Unknown')}\nContent: {d.page_content}" for d in docs])

    rag_chain = (
        {"context": itemgetter("question") | retriever | format_docs, "question": itemgetter("question"), "user_role": itemgetter("user_role")}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain

# --- 3. EXECUTION BLOCK (To allow direct running) ---

if __name__ == "__main__":
    # This block executes if you run 'python rag_pipeline.py' directly
    create_vector_store()