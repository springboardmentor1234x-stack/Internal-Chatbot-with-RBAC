from typing import List, Dict, Any

SYSTEM_PROMPT = """You are a secure internal company assistant.

RULES (MANDATORY):
- Use ONLY the provided context
- Do NOT guess, infer, or add external knowledge
- Do NOT reveal information from unauthorized departments
- If the answer is missing, say: "I don't have enough information in the accessible documents."
- Cite sources using [chunk_id]

ACCESS:
- Role: {role}
- Allowed Departments: {departments}

Be concise, factual, and professional.
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

ANSWER:"""
        
        return prompt
    
    def build_confidence_message(self, avg_similarity: float) -> str:
        if avg_similarity >= 0.7:
            return "High confidence - strong semantic match"
        elif avg_similarity >= 0.5:
            return "Medium confidence - moderate semantic match"
        elif avg_similarity >= 0.3:
            return "Low confidence - weak semantic match"
        else:
            return "Very low confidence - consider rephrasing your question"
    
    def extract_citations(self, llm_response: str) -> List[str]:
        import re
        
        # Find all [chunk_id] patterns
        pattern = r'\[([^\]]+)\]'
        citations = re.findall(pattern, llm_response)
        
        return citations