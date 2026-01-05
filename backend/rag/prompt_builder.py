from typing import List, Dict, Any

SYSTEM_PROMPT = """You are a secure company internal assistant with role-based access control.

CRITICAL RULES:
1. Answer ONLY using the provided context documents
2. NEVER fabricate, assume, or infer information not in the context
3. NEVER leak information from departments the user cannot access
4. If the answer is not in the provided context, explicitly state: "I don't have enough information in the accessible documents to answer this question."
5. Always cite your sources using [chunk_id] notation
6. Be concise, professional, and accurate

ROLE RESTRICTIONS:
- User Role: {role}
- Accessible Departments: {departments}
- You can ONLY provide information from these departments
"""

class PromptBuilder:
    """Build prompts for LLM with context and system instructions"""
    
    def __init__(self):
        self.system_prompt = SYSTEM_PROMPT
    
    def build_rag_prompt(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        role: str,
        accessible_departments: List[str]
    ) -> str:
        """
        Build complete RAG prompt with system instructions and context
        
        Args:
            query: User's query
            context_chunks: Retrieved document chunks
            role: User's role
            accessible_departments: Departments user can access
            
        Returns:
            Complete prompt string
        """
        # Build context section from chunks
        context_parts = []
        for chunk in context_chunks:
            metadata = chunk.get("metadata", {})
            source_doc = metadata.get("source_document", "Unknown")
            department = metadata.get("department", "Unknown")
            chunk_id = chunk.get("id", "unknown")
            content = chunk.get("content", "")
            
            context_part = (
                f"[Source: {source_doc} | Department: {department} | Chunk ID: {chunk_id}]\n"
                f"{content}"
            )
            context_parts.append(context_part)
        
        context_text = "\n\n".join(context_parts)
        departments_str = ", ".join(accessible_departments)
        
        # Build complete prompt
        prompt = f"""{self.system_prompt.format(role=role, departments=departments_str)}

CONTEXT DOCUMENTS:
{context_text}

USER QUESTION: {query}

INSTRUCTIONS:
- Provide a clear, concise answer based ONLY on the context above
- Cite sources using [chunk_id] format
- If information is not available, say so explicitly
- Do not speculate or add information beyond the context

ANSWER:"""
        
        return prompt
    
    def build_confidence_message(self, avg_similarity: float) -> str:
        """
        Generate confidence message based on average similarity score
        
        Args:
            avg_similarity: Average similarity score of retrieved chunks
            
        Returns:
            Confidence message string
        """
        if avg_similarity >= 0.7:
            return "High confidence - strong semantic match"
        elif avg_similarity >= 0.5:
            return "Medium confidence - moderate semantic match"
        elif avg_similarity >= 0.3:
            return "Low confidence - weak semantic match"
        else:
            return "Very low confidence - consider rephrasing your question"
    
    def extract_citations(self, llm_response: str) -> List[str]:
        """
        Extract chunk_id citations from LLM response
        
        Args:
            llm_response: Generated response from LLM
            
        Returns:
            List of cited chunk IDs
        """
        import re
        
        # Find all [chunk_id] patterns
        pattern = r'\[([^\]]+)\]'
        citations = re.findall(pattern, llm_response)
        
        return citations