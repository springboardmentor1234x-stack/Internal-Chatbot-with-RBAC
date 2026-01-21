"""
Document Chunker - Split documents into manageable chunks
Chunks are 300-512 tokens with overlap for context preservation
"""

import re
from typing import List, Dict, Any
import tiktoken


class DocumentChunker:
    """Split documents into chunks with metadata"""
    
    def __init__(self, 
                 chunk_size: int = 512,
                 chunk_overlap: int = 50,
                 encoding_name: str = "cl100k_base"):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target size in tokens (300-512)
            chunk_overlap: Overlap between chunks in tokens
            encoding_name: Tiktoken encoding to use
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize tokenizer (using tiktoken for accurate token counting)
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
        except:
            # Fallback to simple word-based splitting
            self.encoding = None
            print("⚠️  Tiktoken not available, using word-based chunking")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        if self.encoding:
            return len(self.encoding.encode(text))
        else:
            # Fallback: estimate tokens as ~0.75 * words
            return int(len(text.split()) * 0.75)
    
    def chunk_by_tokens(self, text: str) -> List[str]:
        """
        Chunk text by token count
        """
        if not text:
            return []
        
        if self.encoding:
            # Use tiktoken for precise chunking
            tokens = self.encoding.encode(text)
            chunks = []
            
            start = 0
            while start < len(tokens):
                end = start + self.chunk_size
                chunk_tokens = tokens[start:end]
                chunk_text = self.encoding.decode(chunk_tokens)
                chunks.append(chunk_text)
                
                # Move start forward with overlap
                start = end - self.chunk_overlap
            
            return chunks
        else:
            # Fallback: word-based chunking
            words = text.split()
            # Approximate chunk size in words (tokens ≈ 0.75 * words)
            word_chunk_size = int(self.chunk_size / 0.75)
            word_overlap = int(self.chunk_overlap / 0.75)
            
            chunks = []
            start = 0
            while start < len(words):
                end = start + word_chunk_size
                chunk_words = words[start:end]
                chunk_text = ' '.join(chunk_words)
                chunks.append(chunk_text)
                
                start = end - word_overlap
            
            return chunks
    
    def chunk_by_paragraphs(self, text: str, max_tokens: int = None) -> List[str]:
        """
        Chunk text by paragraphs, combining until reaching max_tokens
        """
        if max_tokens is None:
            max_tokens = self.chunk_size
        
        # Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\n+', text)
        
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_tokens = self.count_tokens(para)
            
            # If single paragraph exceeds max_tokens, split it
            if para_tokens > max_tokens:
                # Save current chunk if exists
                if current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
                
                # Split long paragraph
                para_chunks = self.chunk_by_tokens(para)
                chunks.extend(para_chunks)
            else:
                # Check if adding this paragraph exceeds limit
                if current_tokens + para_tokens > max_tokens:
                    # Save current chunk
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [para]
                    current_tokens = para_tokens
                else:
                    # Add to current chunk
                    current_chunk.append(para)
                    current_tokens += para_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunks.append('\n\n'.join(current_chunk))
        
        return chunks
    
    def chunk_document(self, 
                       document: Dict[str, Any],
                       strategy: str = 'paragraph') -> List[Dict[str, Any]]:
        """
        Chunk a document with metadata
        
        Args:
            document: Parsed document dict
            strategy: 'paragraph' or 'token'
        
        Returns:
            List of chunk dicts with metadata
        """
        text = document.get('content', '')
        
        if strategy == 'paragraph':
            chunks = self.chunk_by_paragraphs(text)
        else:
            chunks = self.chunk_by_tokens(text)
        
        # Create chunk dicts with metadata
        chunk_dicts = []
        for i, chunk_text in enumerate(chunks):
            chunk_dict = {
                'chunk_id': f"{document['filename']}_{i}",
                'text': chunk_text,
                'token_count': self.count_tokens(chunk_text),
                'chunk_index': i,
                'total_chunks': len(chunks),
                'source_document': document['filename'],
                'department': document['department'],
                'document_title': document.get('title', document['filename']),
            }
            chunk_dicts.append(chunk_dict)
        
        return chunk_dicts


def main():
    """Test the chunker"""
    print("=" * 60)
    print("DOCUMENT CHUNKER TEST")
    print("=" * 60)
    
    chunker = DocumentChunker(chunk_size=512, chunk_overlap=50)
    
    # Test text
    test_doc = {
        'filename': 'test_doc.md',
        'department': 'Finance',
        'title': 'Test Document',
        'content': """
Financial Report for 2024

Executive Summary:
This is the first paragraph with important financial information.
It contains revenue data and expense analysis.

Year-Over-Year Analysis:
Revenue grew by 25% in 2024. This is significant growth.
Operating expenses increased by 18%.

The company maintains strong cash flow position.
Profit margins improved by 3 percentage points.

Conclusion:
Overall performance exceeded expectations.
The outlook for 2025 remains positive.
        """.strip()
    }
    
    print(f"\n📄 Original document: {len(test_doc['content'])} characters")
    print(f"   Tokens: {chunker.count_tokens(test_doc['content'])}")
    
    # Test paragraph chunking
    chunks = chunker.chunk_document(test_doc, strategy='paragraph')
    
    print(f"\n📦 Created {len(chunks)} chunks:\n")
    
    for chunk in chunks:
        print(f"Chunk {chunk['chunk_index'] + 1}/{chunk['total_chunks']}")
        print(f"  ID: {chunk['chunk_id']}")
        print(f"  Tokens: {chunk['token_count']}")
        print(f"  Text preview: {chunk['text'][:100]}...")
        print()
    
    print("=" * 60)
    print("✅ Chunking complete")


if __name__ == "__main__":
    main()
