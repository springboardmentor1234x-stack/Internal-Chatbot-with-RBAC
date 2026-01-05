import os
from typing import List, Dict
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# --- CONFIGURATION ---
RAW_DATA_PATH = "./data/raw"
CHROMA_PATH = "./data/chroma"

# Document-to-Role Mapping with Citation Metadata
DOCUMENT_MAP = {
    "quarterly_financial_report.md": {
        "roles": ["Finance", "C-Level"],
        "title": "Quarterly Financial Report - FinSolve Technologies Inc. 2024",
        "author": "FinSolve Finance Department",
        "date": "2024-12-31",
        "type": "Financial Report"
    },
    "market_report_q4_2024.md": {
        "roles": ["Marketing", "C-Level"],
        "title": "Q4 2024 Marketing Performance Report",
        "author": "FinSolve Marketing Department",
        "date": "2024-12-31",
        "type": "Marketing Report"
    },
    "employee_handbook.md": {
        "roles": ["HR", "Employee", "C-Level", "Finance", "Marketing", "Engineering"],
        "title": "Employee Handbook - FinSolve Technologies",
        "author": "FinSolve HR Department",
        "date": "2024-01-01",
        "type": "Policy Document"
    },
    "engineering_master_doc.md": {
        "roles": ["Engineering", "C-Level"],
        "title": "Engineering Master Documentation",
        "author": "FinSolve Engineering Department",
        "date": "2024-06-15",
        "type": "Technical Documentation"
    },
}


class SimpleRAGPipeline:
    def __init__(self):
        self.documents = {}
        self.load_documents()

    def load_documents(self):
        """Load documents from the data directory with citation metadata."""
        if not os.path.exists(RAW_DATA_PATH):
            print(f"Data path {RAW_DATA_PATH} does not exist.")
            return

        for filename in os.listdir(RAW_DATA_PATH):
            if filename.endswith(".md"):
                file_path = os.path.join(RAW_DATA_PATH, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Get document metadata for citations
                    doc_metadata = DOCUMENT_MAP.get(filename, {
                        "roles": ["Employee"],
                        "title": filename.replace("_", " ").replace(".md", "").title(),
                        "author": "FinSolve Technologies",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "type": "Document"
                    })

                    # Store document with role information and metadata
                    allowed_roles = doc_metadata["roles"]
                    self.documents[filename] = {
                        "content": content,
                        "allowed_roles": allowed_roles,
                        "metadata": doc_metadata
                    }
                    print(f"Loaded: {filename}")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")

    def _generate_citation(self, filename: str) -> str:
        """Generate simple citation for a document."""
        if filename not in self.documents:
            return f"Source: {filename}"
        
        metadata = self.documents[filename].get("metadata", {})
        author = metadata.get("author", "FinSolve Technologies")
        date = metadata.get("date", "2024")
        title = metadata.get("title", filename.replace("_", " ").replace(".md", "").title())
        doc_type = metadata.get("type", "Document")
        
        # Simple citation format: Author (Date). Title. [Document Type].
        return f"{author} ({date}). {title}. [{doc_type}]."

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
                lines = doc_data["content"].split("\n")
                relevant_lines = []

                for line in lines:
                    if any(word in line.lower() for word in query_lower.split()):
                        relevant_lines.append(line.strip())

                if relevant_lines:
                    snippet = "\n".join(relevant_lines[:3])  # First 3 relevant lines
                    results.append(
                        {
                            "source": filename,
                            "content": snippet,
                            "score": len(relevant_lines),
                        }
                    )

        # Sort by relevance (number of matching lines)
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]  # Top 5 results

    def run_pipeline(self, query: str, user_role: str) -> Dict:
        """
        Run the simple RAG pipeline with role-based filtering and citations.
        """
        try:
            # Perform simple search
            results = self.simple_search(query, user_role)

            if not results:
                return {
                    "response": f"No relevant information found for your role ({user_role}). You may not have access to the requested information.",
                    "sources": [],
                    "citations": [],
                    "error": "No accessible documents found",
                }

            # Extract sources and generate citations
            sources = [result["source"] for result in results]
            citations = [self._generate_citation(result["source"]) for result in results]

            # Generate response with citations
            response_parts = []
            response_parts.append(
                f"Based on the available documents for your role ({user_role}), here's what I found:"
            )
            response_parts.append("")

            for i, result in enumerate(results[:3], 1):
                source_title = self.documents[result["source"]]["metadata"].get("title", result["source"])
                response_parts.append(f"**{i}. From {source_title}:**")
                
                content_preview = (
                    result["content"][:200] + "..."
                    if len(result["content"]) > 200
                    else result["content"]
                )
                response_parts.append(f"• {content_preview}")
                
                # Add inline citation reference
                response_parts.append(f"  *Source: [{i}] See references below*")
                response_parts.append("")

            # Add citations section
            if citations:
                response_parts.append("**References:**")
                for i, citation in enumerate(citations[:3], 1):
                    response_parts.append(f"[{i}] {citation}")

            response = "\n".join(response_parts)

            return {
                "response": response, 
                "sources": sources, 
                "citations": citations,
                "error": None
            }

        except Exception as e:
            print(f"Error in RAG pipeline: {e}")
            return {
                "response": "An error occurred while processing your request. Please try again.",
                "sources": [],
                "citations": [],
                "error": str(e),
            }


# Global instance
rag_pipeline = SimpleRAGPipeline()
