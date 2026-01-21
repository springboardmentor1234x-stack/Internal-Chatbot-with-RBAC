"""
Prompt Templates for RAG System
Role-aware, RBAC-compliant prompts with citation requirements
"""

from typing import List, Dict


class PromptTemplates:
    """Centralized prompt templates for RAG system"""
    
    @staticmethod
    def get_system_prompt(user_role: str, accessible_departments: List[str]) -> str:
        """
        Generate role-aware system prompt
        
        Args:
            user_role: User's role (e.g., "finance_employee")
            accessible_departments: Departments user can access
        
        Returns:
            System prompt string
        """
        return f"""You are a secure AI assistant for an internal company chatbot system.

ROLE & ACCESS:
- User Role: {user_role}
- Accessible Departments: {', '.join(accessible_departments)}
- Access Level: {"Full Access (Admin)" if user_role == "admin" else "Department-Specific"}

STRICT RULES (MANDATORY):
1. Use ONLY the provided context documents to answer
2. Do NOT guess, infer, or add external knowledge
3. Do NOT reveal information from unauthorized departments
4. If the answer is not in the context, say: "I don't have enough information in the accessible documents to answer this question."
5. ALWAYS cite sources using [chunk_id] format
6. Be concise, factual, and professional
7. Use bullet points for clarity when listing multiple items
8. Do NOT repeat the same information from different chunks

CITATION FORMAT:
- Every factual claim must have a citation: "Revenue was $5M [chunk_123]"
- Multiple sources: "Sales increased by 20% [chunk_456] and profits rose by 15% [chunk_789]"

RESPONSE STRUCTURE:
1. Direct answer to the question
2. Supporting details with citations
3. If relevant, mention which department(s) the information comes from

Remember: You can ONLY access and discuss information from {', '.join(accessible_departments)} department(s).
"""
    
    @staticmethod
    def get_user_prompt(query: str, context_chunks: List[Dict], user_role: str) -> str:
        """
        Generate user prompt with context
        
        Args:
            query: User's query
            context_chunks: Retrieved and filtered chunks with metadata
            user_role: User's role for context
        
        Returns:
            User prompt with formatted context
        """
        # Format context chunks
        context_parts = []
        for idx, chunk in enumerate(context_chunks, 1):
            chunk_id = chunk.get('id', f'chunk_{idx}')
            text = chunk.get('text', '')
            department = chunk.get('department', 'Unknown')
            source = chunk.get('source', 'Unknown')
            
            context_parts.append(f"""[{chunk_id}]
Department: {department}
Source: {source}
Content: {text}
""")
        
        full_context = "\n---\n".join(context_parts)
        
        return f"""CONTEXT DOCUMENTS:
{full_context}

---

USER QUESTION:
{query}

INSTRUCTIONS:
Answer the question using ONLY the context documents provided above. Include [chunk_id] citations for all facts. Be concise and professional."""
    
    @staticmethod
    def get_no_context_prompt(query: str, user_role: str, accessible_departments: List[str]) -> str:
        """
        Prompt when no relevant context is found
        
        Args:
            query: User's query
            user_role: User's role
            accessible_departments: Departments user can access
        
        Returns:
            Appropriate response prompt
        """
        return f"""I don't have enough information in the accessible documents to answer your question about: "{query}"

As a {user_role}, you have access to information from: {', '.join(accessible_departments)}.

The available documents in these departments don't contain information relevant to your query. This could mean:
1. The information is not available in your accessible departments
2. The information might exist in other departments you don't have access to
3. The information hasn't been added to the system yet

Please try:
- Rephrasing your question
- Being more specific
- Asking about topics within your accessible departments
"""
    
    @staticmethod
    def get_confidence_prompt(answer: str) -> str:
        """
        Prompt to assess confidence in the generated answer
        
        Args:
            answer: Generated answer
        
        Returns:
            Confidence assessment prompt
        """
        return f"""Given the following answer generated from retrieved documents:

"{answer}"

On a scale of 0-100%, how confident are you that this answer:
1. Directly addresses the user's question
2. Is fully supported by the provided context
3. Contains no external knowledge or guessing

Provide ONLY a number between 0-100. No explanation needed.
"""
    
    @staticmethod
    def format_final_response(
        answer: str,
        sources: List[Dict],
        confidence: float,
        metadata: Dict
    ) -> Dict:
        """
        Format the final response with all components
        
        Args:
            answer: Generated answer text
            sources: Source information list
            confidence: Confidence score (0-1)
            metadata: Additional metadata
        
        Returns:
            Formatted response dictionary
        """
        return {
            "answer": answer,
            "sources": sources,
            "confidence": round(confidence * 100, 2),
            "confidence_level": (
                "HIGH" if confidence >= 0.8 else
                "MEDIUM" if confidence >= 0.5 else
                "LOW"
            ),
            "metadata": {
                **metadata,
                "response_type": "llm_generated",
                "has_citations": "[chunk_" in answer or "[source_" in answer
            }
        }


# Example usage and testing
if __name__ == "__main__":
    templates = PromptTemplates()
    
    # Test system prompt
    print("=== SYSTEM PROMPT ===")
    print(templates.get_system_prompt("finance_employee", ["Finance", "General"]))
    print("\n")
    
    # Test user prompt
    print("=== USER PROMPT ===")
    test_chunks = [
        {
            "id": "chunk_001",
            "text": "Q4 2024 revenue was $5.2M, up 15% from Q3.",
            "department": "Finance",
            "source": "quarterly_financial_report.md"
        },
        {
            "id": "chunk_002",
            "text": "Operating expenses decreased by 8% to $3.1M.",
            "department": "Finance",
            "source": "financial_summary.md"
        }
    ]
    print(templates.get_user_prompt(
        "What was the Q4 revenue?",
        test_chunks,
        "finance_employee"
    ))
    print("\n")
    
    # Test no context prompt
    print("=== NO CONTEXT PROMPT ===")
    print(templates.get_no_context_prompt(
        "What is the marketing budget?",
        "finance_employee",
        ["Finance", "General"]
    ))
