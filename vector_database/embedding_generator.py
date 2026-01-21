"""
Embedding Generator - Generate vector embeddings for document chunks
Uses sentence-transformers for local embedding generation
"""

from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import json
from pathlib import Path
import numpy as np


class EmbeddingGenerator:
    """Generate embeddings using sentence-transformers"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding generator
        
        Args:
            model_name: HuggingFace model name for embeddings
        """
        self.model_name = model_name
        print(f"📥 Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"✅ Model loaded! Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
        
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector as list of floats
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of input texts
            batch_size: Batch size for encoding
            
        Returns:
            List of embedding vectors
        """
        print(f"🔄 Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add embeddings to chunk dictionaries
        
        Args:
            chunks: List of chunk dicts with 'text' field
            
        Returns:
            Chunks with added 'embedding' field
        """
        # Extract texts
        texts = [chunk['text'] for chunk in chunks]
        
        # Generate embeddings in batch
        embeddings = self.generate_embeddings_batch(texts)
        
        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = embeddings[i]
        
        print(f"✅ Added embeddings to {len(chunks)} chunks")
        return chunks
    
    def save_embeddings(self, chunks: List[Dict[str, Any]], output_file: str):
        """
        Save chunks with embeddings to file
        
        Args:
            chunks: Chunks with embeddings
            output_file: Output file path
        """
        output_path = Path(output_file)
        
        with open(output_path, 'w') as f:
            json.dump(chunks, f, indent=2)
        
        print(f"💾 Saved {len(chunks)} chunks with embeddings to: {output_path}")
        
        # Also save metadata summary
        summary = {
            'total_chunks': len(chunks),
            'embedding_dimension': len(chunks[0]['embedding']) if chunks else 0,
            'model_name': self.model_name,
            'chunks_by_department': {}
        }
        
        # Count by department
        for chunk in chunks:
            dept = chunk.get('department', 'Unknown')
            summary['chunks_by_department'][dept] = summary['chunks_by_department'].get(dept, 0) + 1
        
        summary_file = output_path.parent / f"{output_path.stem}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Saved summary to: {summary_file}")


def main():
    """Test embedding generation"""
    print("=" * 60)
    print("EMBEDDING GENERATOR TEST")
    print("=" * 60)
    
    # Load processed chunks from Module 2
    chunks_file = "../module_2_document_preprocessing/chunks_for_embedding.json"
    
    if not Path(chunks_file).exists():
        print(f"❌ Error: {chunks_file} not found")
        print("   Please run Module 2 first to generate chunks")
        return
    
    print(f"\n📂 Loading chunks from: {chunks_file}")
    with open(chunks_file, 'r') as f:
        chunks = json.load(f)
    
    print(f"✅ Loaded {len(chunks)} chunks")
    
    # Initialize generator
    generator = EmbeddingGenerator()
    
    # Generate embeddings
    chunks_with_embeddings = generator.embed_chunks(chunks)
    
    # Save results
    generator.save_embeddings(chunks_with_embeddings, "chunks_with_embeddings.json")
    
    # Display sample
    print("\n📊 Sample Embedding:")
    sample = chunks_with_embeddings[0]
    print(f"   Chunk ID: {sample['chunk_id']}")
    print(f"   Text preview: {sample['text'][:100]}...")
    print(f"   Embedding dimension: {len(sample['embedding'])}")
    print(f"   First 5 values: {sample['embedding'][:5]}")
    
    print("\n" + "=" * 60)
    print("✅ Embedding generation complete!")


if __name__ == "__main__":
    main()
