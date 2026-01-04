import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import json

load_dotenv()

# --- CONFIGURATION ---
RAW_DATA_PATH = "./data/raw"
CHROMA_PATH = "./data/chroma" 

# Document-to-Role Mapping
DOCUMENT_MAP = {
    "quarterly_financial_report.md": ["Finance", "C-Level"],
    "market_report_q4_2024.md": ["Marketing", "C-Level"],
    "employee_handbook.md": ["HR", "Employee", "C-Level", "Finance", "Marketing", "Engineering"], 
    "engineering_master_doc.md": ["Engineering", "C-Level"],
}

class SimpleRAGPipeline:
    def __init__(self):
        self.documents = {}
        self.load_documents()
    
    def load_documents(self):
        """Load documents from the data directory."""
        if not os.path.exists(RAW_DATA_PATH):
            print(f"Data path {RAW_DATA_PATH} does not exist.")
            return
        
        for filename in os.listdir(RAW_DATA_PATH):
            if filename.endswith('.md'):
                file_path = os.path.join(RAW_DATA_PATH, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Store document with role information
                    allowed_roles = DOCUMENT_MAP.get(filename, ["Employee"])
                    self.documents[filename] = {
                        "content": content,
                        "allowed_roles": allowed_roles
                    }
                    print(f"Loaded: {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
    
    def simple_search(self, query: str, user_role: str) -> List[Dict]:
        """Simple keyword-based search."""
        results = []
        query_lower = query.lower()
        
        for filename, doc_data in self.documents.items():
            # Check if user has access to this document
            if user_role not in doc_data["allowed_roles"]:
                continue
            
            content = doc_data["content"].lower()
            
            # Simple keyword matching
            if any(word in content for word in query_lower.split()):
                # Extract relevant snippet
                lines = doc_data["content"].split('\n')
                relevant_lines = []
                
                for line in lines:
                    if any(word in line.lower() for word in query_lower.split()):
                        relevant_lines.append(line.strip())
                
                if relevant_lines:
                    snippet = '\n'.join(relevant_lines[:3])  # First 3 relevant lines
                    results.append({
                        "source": filename,
                        "content": snippet,
                        "score": len(relevant_lines)
                    })
        
        # Sort by relevance (number of matching lines)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]  # Top 5 results
    
    def run_pipeline(self, query: str, user_role: str) -> Dict:
        """
        Run the simple RAG pipeline with role-based filtering.
        """
        try:
            # Perform simple search
            results = self.simple_search(query, user_role)
            
            if not results:
                return {
                    "response": f"No relevant information found for your role ({user_role}). You may not have access to the requested information.",
                    "sources": [],
                    "error": "No accessible documents found"
                }
            
            # Extract sources
            sources = [result["source"] for result in results]
            
            # Generate simple response
            response_parts = []
            response_parts.append(f"Based on the available documents for your role ({user_role}), here's what I found:")
            response_parts.append("")
            
            for i, result in enumerate(results[:3], 1):
                response_parts.append(f"{i}. From {result['source']}:")
                response_parts.append(result['content'][:200] + "..." if len(result['content']) > 200 else result['content'])
                response_parts.append("")
            
            response = "\n".join(response_parts)
            
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
rag_pipeline = SimpleRAGPipeline()