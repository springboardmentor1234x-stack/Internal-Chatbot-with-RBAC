"""
Response Formatter
Formats LLM responses with proper citations and source attribution
"""

import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Format LLM responses with citations and source attribution"""
    
    def __init__(self):
        """Initialize response formatter"""
        pass
    
    def format_response(
        self,
        answer: str,
        sources: List[Dict[str, Any]],
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Format complete response with citations
        
        Args:
            answer: LLM-generated answer
            sources: List of source documents
            metadata: Additional metadata
        
        Returns:
            Formatted response dictionary
        """
        # Extract and validate citations
        citations = self.extract_citations(answer)
        
        # Format sources
        formatted_sources = self.format_sources(sources)
        
        # Check citation coverage
        has_citations = len(citations) > 0
        citation_rate = len(citations) / max(len(answer.split('.')), 1)
        
        return {
            "answer": answer,
            "sources": formatted_sources,
            "citations": citations,
            "has_citations": has_citations,
            "citation_count": len(citations),
            "citation_rate": round(citation_rate, 3),
            "metadata": metadata or {}
        }
    
    def extract_citations(self, text: str) -> List[str]:
        """
        Extract citation markers from text
        
        Args:
            text: Text with citations like [chunk_001] or [source_1]
        
        Returns:
            List of unique citation IDs
        """
        # Pattern to match [chunk_xxx] or [source_xxx]
        pattern = r'\[(chunk|source)_\w+\]'
        
        matches = re.findall(pattern, text.lower())
        citations = [f"[{match}_ID]" for match in matches]
        
        # Return unique citations
        return list(set(citations))
    
    def format_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format source information for display
        
        Args:
            sources: Raw source documents
        
        Returns:
            Formatted source list
        """
        formatted = []
        
        for idx, source in enumerate(sources, 1):
            formatted_source = {
                "id": source.get('id', source.get('chunk_id', f"source_{idx}")),
                "department": source.get('department', 'Unknown'),
                "source_file": source.get('source_file', source.get('source', 'Unknown')),
                "chunk_index": source.get('chunk_index', idx - 1),
                "relevance_score": round(source.get('rerank_score', source.get('score', 0)), 4),
                "preview": self.create_preview(source.get('text', source.get('content', '')), max_length=200)
            }
            formatted.append(formatted_source)
        
        return formatted
    
    def create_preview(self, text: str, max_length: int = 200) -> str:
        """
        Create text preview with ellipsis
        
        Args:
            text: Full text
            max_length: Maximum preview length
        
        Returns:
            Preview string
        """
        if len(text) <= max_length:
            return text
        
        # Find last complete word within limit
        preview = text[:max_length]
        last_space = preview.rfind(' ')
        
        if last_space > 0:
            preview = preview[:last_space]
        
        return preview + "..."
    
    def validate_citations(self, answer: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate that all citations in answer match provided sources
        
        Args:
            answer: LLM-generated answer
            sources: Source documents
        
        Returns:
            Validation results
        """
        cited_ids = self.extract_citations(answer)
        source_ids = [source.get('id', '') for source in sources]
        
        # Check which citations are valid
        valid_citations = [cid for cid in cited_ids if any(cid in sid for sid in source_ids)]
        invalid_citations = [cid for cid in cited_ids if cid not in valid_citations]
        
        # Check which sources were cited
        cited_sources = [src for src in sources if any(src.get('id', '') in cid for cid in cited_ids)]
        uncited_sources = [src for src in sources if src not in cited_sources]
        
        return {
            "total_citations": len(cited_ids),
            "valid_citations": len(valid_citations),
            "invalid_citations": len(invalid_citations),
            "invalid_citation_ids": invalid_citations,
            "cited_sources_count": len(cited_sources),
            "uncited_sources_count": len(uncited_sources),
            "citation_coverage": round(len(cited_sources) / max(len(sources), 1), 2)
        }
    
    def add_source_summary(
        self,
        response: Dict[str, Any],
        include_departments: bool = True
    ) -> Dict[str, Any]:
        """
        Add summary of sources to response
        
        Args:
            response: Formatted response
            include_departments: Include department breakdown
        
        Returns:
            Response with source summary
        """
        sources = response.get('sources', [])
        
        summary = {
            "total_sources": len(sources),
            "source_files": list(set(s.get('source_file', '') for s in sources)),
        }
        
        if include_departments:
            departments = [s.get('department', 'Unknown') for s in sources]
            dept_counts = {}
            for dept in departments:
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
            summary["departments"] = dept_counts
        
        response['source_summary'] = summary
        return response
    
    def format_for_display(self, response: Dict[str, Any]) -> str:
        """
        Format response for text display
        
        Args:
            response: Formatted response dictionary
        
        Returns:
            Human-readable text format
        """
        lines = []
        
        # Answer
        lines.append("=" * 60)
        lines.append("ANSWER:")
        lines.append("=" * 60)
        lines.append(response.get('answer', ''))
        lines.append("")
        
        # Sources
        sources = response.get('sources', [])
        if sources:
            lines.append("=" * 60)
            lines.append(f"SOURCES ({len(sources)}):")
            lines.append("=" * 60)
            
            for i, source in enumerate(sources, 1):
                lines.append(f"\n[{i}] {source.get('id', 'Unknown')}")
                lines.append(f"    Department: {source.get('department', 'Unknown')}")
                lines.append(f"    File: {source.get('source_file', 'Unknown')}")
                lines.append(f"    Relevance: {source.get('relevance_score', 0):.4f}")
                lines.append(f"    Preview: {source.get('preview', 'N/A')}")
        
        # Citation stats
        if response.get('has_citations'):
            lines.append("")
            lines.append("=" * 60)
            lines.append("CITATION STATS:")
            lines.append("=" * 60)
            lines.append(f"Citations found: {response.get('citation_count', 0)}")
            lines.append(f"Citation rate: {response.get('citation_rate', 0):.3f} per sentence")
        
        return "\n".join(lines)


# Test function
if __name__ == "__main__":
    print("🧪 Testing Response Formatter\n")
    
    # Sample data
    answer = """Based on the available financial data, Q4 2024 revenue was $5.2M [chunk_001], representing a 15% increase from Q3 [chunk_001]. Operating expenses decreased by 8% to $3.1M [chunk_002], resulting in improved profit margins."""
    
    sources = [
        {
            "id": "chunk_001",
            "text": "Q4 2024 revenue was $5.2M, up 15% from Q3. This represents strong growth driven by new customer acquisitions and expanded product lines.",
            "department": "Finance",
            "source": "quarterly_financial_report.md",
            "chunk_index": 5,
            "rerank_score": 0.92
        },
        {
            "id": "chunk_002",
            "text": "Operating expenses decreased by 8% to $3.1M through cost optimization initiatives and improved operational efficiency.",
            "department": "Finance",
            "source": "financial_summary.md",
            "chunk_index": 12,
            "rerank_score": 0.85
        },
        {
            "id": "chunk_003",
            "text": "Marketing spent $500K in Q4 with strong ROI of 25% across all campaigns.",
            "department": "Marketing",
            "source": "marketing_report.md",
            "chunk_index": 3,
            "rerank_score": 0.45
        }
    ]
    
    # Initialize formatter
    formatter = ResponseFormatter()
    
    # Format response
    print("📝 Formatting response...\n")
    formatted = formatter.format_response(answer, sources, {"model": "mistral"})
    
    # Display
    print(formatter.format_for_display(formatted))
    
    # Validate citations
    print("\n\n🔍 Citation Validation:\n")
    validation = formatter.validate_citations(answer, sources)
    for key, value in validation.items():
        print(f"  {key}: {value}")
    
    # Add summary
    print("\n\n📊 Adding Source Summary:\n")
    with_summary = formatter.add_source_summary(formatted)
    summary = with_summary.get('source_summary', {})
    for key, value in summary.items():
        print(f"  {key}: {value}")
