"""
Complete Document Preprocessing Pipeline
Orchestrates parsing, cleaning, chunking, and metadata tagging
"""

import json
import sys
import io
from pathlib import Path
from typing import List, Dict, Any
from document_parser import DocumentParser
from text_cleaner import TextCleaner
from document_chunker import DocumentChunker
from metadata_tagger import MetadataTagger

# Fix Windows encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class PreprocessingPipeline:
    """Complete preprocessing pipeline for RAG documents"""
    
    def __init__(self,
                 dataset_path: str = "../Dataset",
                 role_mapping_file: str = "../module_1_environment_setup/role_document_mapping.json",
                 chunk_size: int = 512,
                 chunk_overlap: int = 50):
        """
        Initialize preprocessing pipeline
        
        Args:
            dataset_path: Path to Dataset directory
            role_mapping_file: Path to role mapping JSON
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks
        """
        self.dataset_path = dataset_path
        
        # Initialize components
        self.parser = DocumentParser(dataset_path)
        self.cleaner = TextCleaner()
        self.chunker = DocumentChunker(chunk_size, chunk_overlap)
        self.tagger = MetadataTagger(role_mapping_file)
        
        # Storage
        self.parsed_docs = []
        self.chunks = []
    
    def parse_documents(self) -> List[Dict[str, Any]]:
        """Step 1: Parse all documents"""
        print("\n" + "=" * 60)
        print("STEP 1: PARSING DOCUMENTS")
        print("=" * 60)
        
        self.parsed_docs = self.parser.parse_all_documents()
        
        print(f"\n✅ Parsed {len(self.parsed_docs)} documents")
        return self.parsed_docs
    
    def clean_documents(self) -> List[Dict[str, Any]]:
        """Step 2: Clean document text"""
        print("\n" + "=" * 60)
        print("STEP 2: CLEANING TEXT")
        print("=" * 60)
        
        for doc in self.parsed_docs:
            original_length = len(doc['content'])
            
            # Clean the content
            cleaned = self.cleaner.clean_text(
                doc['content'],
                normalize_unicode=True,
                remove_urls=False,  # Keep URLs for reference
                mask_emails=True,   # Mask emails for privacy
                remove_special_chars=False,  # Keep punctuation
                normalize_whitespace=True
            )
            
            doc['content'] = cleaned
            doc['cleaned_length'] = len(cleaned)
            
            print(f"✓ Cleaned: {doc['filename']} "
                  f"({original_length:,} → {doc['cleaned_length']:,} chars)")
        
        print(f"\n✅ Cleaned {len(self.parsed_docs)} documents")
        return self.parsed_docs
    
    def chunk_documents(self) -> List[Dict[str, Any]]:
        """Step 3: Chunk documents into segments"""
        print("\n" + "=" * 60)
        print("STEP 3: CHUNKING DOCUMENTS")
        print("=" * 60)
        
        all_chunks = []
        
        for doc in self.parsed_docs:
            # Chunk the document
            doc_chunks = self.chunker.chunk_document(doc, strategy='paragraph')
            all_chunks.extend(doc_chunks)
            
            print(f"✓ Chunked: {doc['filename']} "
                  f"→ {len(doc_chunks)} chunks")
        
        self.chunks = all_chunks
        
        # Calculate statistics
        token_counts = [c['token_count'] for c in all_chunks]
        avg_tokens = sum(token_counts) / len(token_counts) if token_counts else 0
        
        print(f"\n✅ Created {len(all_chunks)} chunks")
        print(f"   Average chunk size: {avg_tokens:.0f} tokens")
        print(f"   Min: {min(token_counts) if token_counts else 0} tokens")
        print(f"   Max: {max(token_counts) if token_counts else 0} tokens")
        
        return all_chunks
    
    def add_metadata(self) -> List[Dict[str, Any]]:
        """Step 4: Add role-based metadata to chunks"""
        print("\n" + "=" * 60)
        print("STEP 4: ADDING METADATA")
        print("=" * 60)
        
        # Tag all chunks
        self.chunks = self.tagger.tag_chunks(self.chunks)
        
        # Get statistics
        stats = self.tagger.get_metadata_stats(self.chunks)
        
        print(f"\n✅ Tagged {stats['total_chunks']} chunks")
        print(f"\n📊 Distribution by department:")
        for dept, count in stats['by_department'].items():
            print(f"   {dept}: {count} chunks")
        
        print(f"\n📊 Accessibility by role:")
        for role, count in sorted(stats['by_role_access'].items()):
            print(f"   {role}: {count} chunks")
        
        print(f"\n   Average roles per chunk: {stats['avg_roles_per_chunk']:.1f}")
        
        return self.chunks
    
    def save_processed_data(self, output_dir: str = "."):
        """Step 5: Save processed chunks"""
        print("\n" + "=" * 60)
        print("STEP 5: SAVING PROCESSED DATA")
        print("=" * 60)
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save full chunks with all metadata
        chunks_file = output_path / "processed_chunks.json"
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved chunks to: {chunks_file}")
        
        # Save summary statistics
        summary = {
            'total_documents': len(self.parsed_docs),
            'total_chunks': len(self.chunks),
            'documents': [
                {
                    'filename': doc['filename'],
                    'department': doc['department'],
                    'format': doc['format'],
                    'original_length': doc['length'],
                    'cleaned_length': doc.get('cleaned_length', doc['length'])
                }
                for doc in self.parsed_docs
            ],
            'chunks_by_department': self.tagger.get_metadata_stats(self.chunks)['by_department'],
            'chunks_by_role': self.tagger.get_metadata_stats(self.chunks)['by_role_access']
        }
        
        summary_file = output_path / "preprocessing_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"✓ Saved summary to: {summary_file}")
        
        # Save chunks in format ready for embedding (text only)
        embedding_ready = []
        for chunk in self.chunks:
            embedding_ready.append({
                'chunk_id': chunk['chunk_id'],
                'text': chunk['text'],
                'metadata': chunk['metadata']
            })
        
        embedding_file = output_path / "chunks_for_embedding.json"
        with open(embedding_file, 'w', encoding='utf-8') as f:
            json.dump(embedding_ready, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved embedding-ready chunks to: {embedding_file}")
        
        print(f"\n✅ All processed data saved to: {output_path}")
    
    def run(self, output_dir: str = "."):
        """
        Run complete preprocessing pipeline
        """
        print("\n" + "╔" + "=" * 58 + "╗")
        print("║" + " " * 15 + "PREPROCESSING PIPELINE" + " " * 21 + "║")
        print("╚" + "=" * 58 + "╝")
        
        # Step 1: Parse
        self.parse_documents()
        
        # Step 2: Clean
        self.clean_documents()
        
        # Step 3: Chunk
        self.chunk_documents()
        
        # Step 4: Add metadata
        self.add_metadata()
        
        # Step 5: Save
        self.save_processed_data(output_dir)
        
        print("\n" + "╔" + "=" * 58 + "╗")
        print("║" + " " * 15 + "PIPELINE COMPLETE! ✅" + " " * 22 + "║")
        print("╚" + "=" * 58 + "╝")
        
        return self.chunks


def main():
    """Run the preprocessing pipeline"""
    pipeline = PreprocessingPipeline(
        dataset_path="../Dataset",
        chunk_size=512,
        chunk_overlap=50
    )
    
    chunks = pipeline.run(output_dir=".")
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"   Total chunks created: {len(chunks)}")
    print(f"   Ready for embedding generation (Module 3)")


if __name__ == "__main__":
    main()
