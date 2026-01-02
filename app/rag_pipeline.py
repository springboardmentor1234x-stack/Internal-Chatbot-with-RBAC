import os
import tiktoken
from typing import List, Dict, Optional
from dotenv import load_dotenv

# LangChain Imports
from langchain_community.document_loaders import UnstructuredMarkdownLoader, CSVLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# --- CONFIGURATION ---
RAW_DATA_PATH = "./data/raw"
PROCESSED_DATA_PATH = "./data/processed"
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
    "employee_handbook.md": ["HR", "Employee", "C-Level", "Finance", "Marketing", "Engineering"], 
    "engineering_master_doc.md": ["Engineering", "C-Level"],
}

class FinSolveRAGPipeline:
    def __init__(self):
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        self.initialize()
    
    def initialize(self):
        """Initialize the RAG pipeline components."""
        try:
            # Initialize OpenAI components
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                print("Warning: OPENAI_API_KEY not found. Using mock responses.")
                return
            
            self.embeddings = OpenAIEmbeddings(
                model=EMBEDDING_MODEL,
                openai_api_key=openai_api_key
            )
            
            self.llm = ChatOpenAI(
                model=LLM_MODEL,
                temperature=LLM_TEMPERATURE,
                openai_api_key=openai_api_key
            )
            
            # Initialize or load vector store
            if os.path.exists(CHROMA_PATH):
                self.vectorstore = Chroma(
                    persist_directory=CHROMA_PATH,
                    embedding_function=self.embeddings
                )
            else:
                print("Vector store not found. Please run setup_vector_store() first.")
                
        except Exception as e:
            print(f"Error initializing RAG pipeline: {e}")
    
    def setup_vector_store(self):
        """Load documents and create vector store."""
        try:
            # Create directories if they don't exist
            os.makedirs(RAW_DATA_PATH, exist_ok=True)
            os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
            os.makedirs(CHROMA_PATH, exist_ok=True)
            
            documents = self.load_documents()
            if not documents:
                print("No documents found to process.")
                return
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len
            )
            
            chunks = text_splitter.split_documents(documents)
            
            # Add role-based metadata to chunks
            for chunk in chunks:
                source_file = os.path.basename(chunk.metadata.get("source", ""))
                allowed_roles = DOCUMENT_MAP.get(source_file, ["Employee"])
                chunk.metadata["allowed_roles"] = allowed_roles
            
            # Create vector store
            if self.embeddings:
                self.vectorstore = Chroma.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    persist_directory=CHROMA_PATH
                )
                self.vectorstore.persist()
                print(f"Vector store created with {len(chunks)} chunks.")
            else:
                print("Embeddings not initialized. Cannot create vector store.")
                
        except Exception as e:
            print(f"Error setting up vector store: {e}")
    
    def load_documents(self) -> List:
        """Load documents from the data directory."""
        documents = []
        
        if not os.path.exists(RAW_DATA_PATH):
            print(f"Data path {RAW_DATA_PATH} does not exist.")
            return documents
        
        for filename in os.listdir(RAW_DATA_PATH):
            file_path = os.path.join(RAW_DATA_PATH, filename)
            
            try:
                if filename.endswith('.md'):
                    loader = UnstructuredMarkdownLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)
                elif filename.endswith('.csv'):
                    loader = CSVLoader(file_path)
                    docs = loader.load()
                    documents.extend(docs)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        
        return documents
    
    def run_pipeline(self, query: str, user_role: str) -> Dict:
        """
        Run the RAG pipeline with role-based filtering.
        """
        try:
            if not self.vectorstore:
                return {
                    "response": "RAG system not properly initialized. Please contact administrator.",
                    "sources": [],
                    "error": "Vector store not available"
                }
            
            # Perform similarity search with role-based filtering
            # Note: Chroma filtering syntax may vary by version
            try:
                # Try modern Chroma filtering
                results = self.vectorstore.similarity_search(
                    query,
                    k=5,
                    filter={"allowed_roles": {"$in": [user_role]}}
                )
            except:
                # Fallback: get all results and filter manually
                all_results = self.vectorstore.similarity_search(query, k=20)
                results = [
                    doc for doc in all_results 
                    if user_role in doc.metadata.get("allowed_roles", [])
                ][:5]
            
            if not results:
                return {
                    "response": f"No relevant information found for your role ({user_role}). You may not have access to the requested information.",
                    "sources": [],
                    "error": "No accessible documents found"
                }
            
            # Extract sources
            sources = list(set([
                os.path.basename(doc.metadata.get("source", "Unknown"))
                for doc in results
            ]))
            
            # Generate response using LLM if available
            if self.llm:
                context = "\n\n".join([doc.page_content for doc in results])
                
                prompt_template = ChatPromptTemplate.from_template("""
                You are a helpful internal company chatbot. Answer the user's question based on the provided context.
                Be concise and professional. If the context doesn't contain enough information, say so.
                
                Context:
                {context}
                
                Question: {question}
                
                Answer:
                """)
                
                chain = prompt_template | self.llm | StrOutputParser()
                response = chain.invoke({"context": context, "question": query})
            else:
                # Fallback response without LLM
                response = f"Based on the available documents, here are the relevant excerpts:\n\n"
                response += "\n\n".join([doc.page_content[:200] + "..." for doc in results[:2]])
            
            return {
                "response": response,
                "sources": sources,
                "error": None
            }
            
        except Exception as e:
            print(f"Error in RAG pipeline: {e}")
            return {
                "response": "An error occurred while processing your request. Please try again.",
                "sources": [],
                "error": str(e)
            }

# Global instance
rag_pipeline = FinSolveRAGPipeline()