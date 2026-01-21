"""
Vector Database Manager - ChromaDB integration with RBAC
Stores embeddings and enables semantic search with role-based filtering
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import json
from pathlib import Path


class VectorDBManager:
    """Manage ChromaDB vector database with RBAC metadata"""
    
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "rag_documents"):
        """
        Initialize ChromaDB
        
        Args:
            persist_directory: Directory to persist database
            collection_name: Name of the collection
        """
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        print(f"🔧 Initializing ChromaDB at: {persist_directory}")
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "RAG documents with RBAC"}
        )
        
        print(f"✅ Collection '{collection_name}' ready")
        print(f"   Current document count: {self.collection.count()}")
    
    def add_documents(self, chunks: List[Dict[str, Any]]):
        """
        Add documents to vector database
        
        Args:
            chunks: List of chunks with embeddings and metadata
        """
        print(f"\n📥 Adding {len(chunks)} documents to vector database...")
        
        # Prepare data for ChromaDB
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            ids.append(chunk['chunk_id'])
            embeddings.append(chunk['embedding'])
            documents.append(chunk['text'])
            
            # Create metadata dict (ChromaDB requires flat dict, no nested structures)
            metadata = {
                'department': chunk['metadata']['department'],
                'source_file': chunk['metadata']['source_file'],
                'chunk_index': chunk['metadata']['chunk_index'],
                'document_title': chunk['metadata']['document_title'],
                # Store accessible roles as comma-separated string
                'accessible_roles': ','.join(chunk['metadata']['accessible_roles'])
            }
            metadatas.append(metadata)
        
        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            batch_end = min(i + batch_size, len(ids))
            
            self.collection.add(
                ids=ids[i:batch_end],
                embeddings=embeddings[i:batch_end],
                documents=documents[i:batch_end],
                metadatas=metadatas[i:batch_end]
            )
            
            print(f"   ✓ Added batch {i//batch_size + 1} ({batch_end}/{len(ids)} documents)")
        
        print(f"✅ Successfully added {len(chunks)} documents")
        print(f"   Total documents in collection: {self.collection.count()}")
    
    def search(self, 
               query_text: str = None,
               query_embedding: List[float] = None,
               n_results: int = 5,
               user_role: str = None,
               department_filter: str = None) -> Dict[str, Any]:
        """
        Search vector database with optional RBAC filtering
        
        Args:
            query_text: Query text (will be embedded)
            query_embedding: Pre-computed query embedding
            n_results: Number of results to return
            user_role: User's role for RBAC filtering
            department_filter: Filter by department
            
        Returns:
            Search results with documents and metadata
        """
        if query_text is None and query_embedding is None:
            raise ValueError("Must provide either query_text or query_embedding")
        
        # Build where filter for RBAC
        where_filter = None
        
        if department_filter:
            where_filter = {"department": department_filter}
        
        # Note: ChromaDB doesn't support complex "contains" queries on string fields
        # For role-based filtering, we'll filter results after retrieval
        
        # Perform search
        if query_embedding:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results * 2,  # Get more results to filter
                where=where_filter,
                include=['documents', 'metadatas', 'distances']
            )
        else:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results * 2,
                where=where_filter,
                include=['documents', 'metadatas', 'distances']
            )
        
        # Apply role-based filtering
        filtered_results = self._apply_rbac_filter(results, user_role, n_results)
        
        return filtered_results
    
    def _apply_rbac_filter(self, results: Dict, user_role: str, n_results: int) -> Dict[str, Any]:
        """
        Filter search results based on user role
        
        Args:
            results: Raw search results from ChromaDB
            user_role: User's role
            n_results: Number of results to return
            
        Returns:
            Filtered results
        """
        if not user_role:
            # No filtering, return all results (limited to n_results)
            limited_ids = results['ids'][0][:n_results]
            return {
                'ids': limited_ids,
                'documents': results['documents'][0][:n_results],
                'metadatas': results['metadatas'][0][:n_results],
                'distances': results['distances'][0][:n_results],
                'count': len(limited_ids)
            }
        
        # Filter by role
        filtered_ids = []
        filtered_docs = []
        filtered_metadata = []
        filtered_distances = []
        
        for i in range(len(results['ids'][0])):
            metadata = results['metadatas'][0][i]
            accessible_roles = metadata.get('accessible_roles', '').split(',')
            
            # Check if user's role is in accessible roles
            if user_role in accessible_roles or user_role == 'admin':
                filtered_ids.append(results['ids'][0][i])
                filtered_docs.append(results['documents'][0][i])
                filtered_metadata.append(metadata)
                filtered_distances.append(results['distances'][0][i])
                
                if len(filtered_ids) >= n_results:
                    break
        
        return {
            'ids': filtered_ids,
            'documents': filtered_docs,
            'metadatas': filtered_metadata,
            'distances': filtered_distances,
            'count': len(filtered_ids)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        total_count = self.collection.count()
        
        # Get sample to analyze departments
        if total_count > 0:
            sample = self.collection.get(limit=total_count, include=['metadatas'])
            
            dept_counts = {}
            for metadata in sample['metadatas']:
                dept = metadata.get('department', 'Unknown')
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
            
            return {
                'total_documents': total_count,
                'collection_name': self.collection_name,
                'by_department': dept_counts
            }
        
        return {
            'total_documents': 0,
            'collection_name': self.collection_name,
            'by_department': {}
        }
    
    def clear_collection(self):
        """Clear all documents from collection"""
        print(f"⚠️  Clearing collection: {self.collection_name}")
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "RAG documents with RBAC"}
        )
        print(f"✅ Collection cleared")


def main():
    """Test vector database"""
    print("=" * 60)
    print("VECTOR DATABASE MANAGER TEST")
    print("=" * 60)
    
    # Initialize database
    db = VectorDBManager()
    
    # Load chunks with embeddings
    chunks_file = "chunks_with_embeddings.json"
    
    if not Path(chunks_file).exists():
        print(f"\n❌ Error: {chunks_file} not found")
        print("   Please run embedding_generator.py first")
        return
    
    print(f"\n📂 Loading chunks from: {chunks_file}")
    with open(chunks_file, 'r') as f:
        chunks = json.load(f)
    
    print(f"✅ Loaded {len(chunks)} chunks with embeddings")
    
    # Clear existing data (for testing)
    if db.collection.count() > 0:
        print("\n🗑️  Clearing existing data...")
        db.clear_collection()
    
    # Add documents
    db.add_documents(chunks)
    
    # Get stats
    stats = db.get_stats()
    print(f"\n📊 Database Statistics:")
    print(f"   Total documents: {stats['total_documents']}")
    print(f"   By department:")
    for dept, count in stats['by_department'].items():
        print(f"      {dept}: {count}")
    
    # Test search
    print(f"\n🔍 Testing search (no RBAC filter):")
    results = db.search(
        query_text="financial revenue and expenses",
        n_results=3
    )
    
    print(f"   Found {results['count']} results:")
    for i, (doc_id, distance) in enumerate(zip(results['ids'], results['distances'])):
        metadata = results['metadatas'][i]
        print(f"\n   {i+1}. {doc_id}")
        print(f"      Distance: {distance:.4f}")
        print(f"      Department: {metadata['department']}")
        print(f"      Preview: {results['documents'][i][:100]}...")
    
    # Test RBAC filtering
    print(f"\n🔐 Testing search with RBAC (finance_employee):")
    results = db.search(
        query_text="financial revenue and expenses",
        n_results=3,
        user_role="finance_employee"
    )
    
    print(f"   Found {results['count']} results:")
    for i, doc_id in enumerate(results['ids']):
        metadata = results['metadatas'][i]
        print(f"   {i+1}. {doc_id} - Department: {metadata['department']}")
    
    print("\n" + "=" * 60)
    print("✅ Vector database test complete!")


if __name__ == "__main__":
    main()
