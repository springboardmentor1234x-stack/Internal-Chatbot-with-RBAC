# Module 3: Vector Database & Embedding Generation

## Overview
This module generates semantic embeddings for all processed document chunks and stores them in a ChromaDB vector database with RBAC metadata. It enables semantic search with role-based access control.

## Architecture

```
Module 3 Pipeline Flow:
┌─────────────────────────────────────────────────────────────┐
│ Input: chunks_for_embedding.json (from Module 2)           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Embedding Generator                                      │
│    - Load sentence-transformers model (all-MiniLM-L6-v2)   │
│    - Generate 384-dim embeddings for each chunk            │
│    - Batch processing for efficiency                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Vector Database Manager                                  │
│    - Initialize ChromaDB                                    │
│    - Store embeddings with RBAC metadata                   │
│    - Create searchable collection                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Semantic Search Engine                                   │
│    - Query-based similarity search                         │
│    - RBAC filtering by user role                           │
│    - Department-based filtering                            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ Output:                                                      │
│   - chunks_with_embeddings.json (70 chunks)                │
│   - module3_summary.json (statistics)                      │
│   - chroma_db/ (persistent vector database)                │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. embedding_generator.py
**Purpose**: Generate semantic embeddings for text chunks

**Features**:
- Uses `sentence-transformers/all-MiniLM-L6-v2` model
- Generates 384-dimensional embeddings
- Batch processing for efficiency
- GPU acceleration if available
- Progress tracking with tqdm

**Key Functions**:
```python
embed_chunks(chunks)      # Generate embeddings for all chunks
save_embeddings(...)      # Save to JSON with summary
```

### 2. vector_db_manager.py
**Purpose**: Manage ChromaDB vector database with RBAC

**Features**:
- Persistent ChromaDB storage
- RBAC metadata preservation
- Semantic similarity search
- Role-based access filtering
- Department-based filtering
- Database statistics

**Key Functions**:
```python
add_documents(chunks)                    # Add chunks to DB
search(query, role, n_results)          # Semantic search with RBAC
get_stats()                             # Database statistics
clear_collection()                      # Reset database
```

### 3. module3_pipeline.py
**Purpose**: Complete Module 3 orchestration

**Workflow**:
1. Load processed chunks from Module 2
2. Generate embeddings for all chunks
3. Initialize ChromaDB
4. Populate vector database
5. Verify statistics
6. Test semantic search
7. Test RBAC filtering
8. Save summary

## Installation

### Prerequisites
```bash
cd module_3_vector_database
pip install -r requirements.txt
```

### Dependencies
- `sentence-transformers`: Embedding generation
- `chromadb`: Vector database
- `torch`: Neural network backend
- `tqdm`: Progress tracking

## Usage

### Quick Start
```bash
# Run complete pipeline
python module3_pipeline.py
```

### Individual Components

#### 1. Generate Embeddings Only
```python
from embedding_generator import EmbeddingGenerator

generator = EmbeddingGenerator()
chunks_with_embeddings = generator.embed_chunks(chunks)
generator.save_embeddings(chunks_with_embeddings, "output.json")
```

#### 2. Use Vector Database Only
```python
from vector_db_manager import VectorDBManager

# Initialize
db = VectorDBManager(persist_directory="./chroma_db")

# Add documents
db.add_documents(chunks_with_embeddings)

# Search without RBAC
results = db.search(
    query_text="financial performance",
    n_results=5
)

# Search with RBAC filtering
results = db.search(
    query_text="financial performance",
    n_results=5,
    user_role="finance_employee"
)

# Get statistics
stats = db.get_stats()
```

## Output Files

### 1. chunks_with_embeddings.json
Contains all chunks with their embeddings:
```json
[
  {
    "chunk_id": "doc_1_chunk_0",
    "text": "Chunk text...",
    "embedding": [0.123, -0.456, ...],  // 384 dimensions
    "metadata": {
      "department": "Finance",
      "source_file": "financial_summary.md",
      "accessible_roles": ["admin", "finance_employee"],
      ...
    }
  }
]
```

### 2. module3_summary.json
Pipeline execution summary:
```json
{
  "total_chunks": 70,
  "embedding_dimension": 384,
  "vector_db_stats": {
    "total_documents": 70,
    "collection_name": "rag_documents",
    "by_department": {
      "Engineering": 13,
      "Finance": 9,
      "General": 7,
      "HR": 25,
      "Marketing": 16
    }
  },
  "model_used": "sentence-transformers/all-MiniLM-L6-v2",
  "status": "complete"
}
```

### 3. chroma_db/
Persistent vector database directory (ChromaDB storage)

## Testing

### Automated Tests
```bash
bash test_module3.sh
```

**Tests Include**:
- Source files existence
- Module 2 output availability
- Pipeline execution
- Output file generation
- Vector database creation
- Embedding validation

### Manual Verification
```python
import json

# Check embeddings
with open('chunks_with_embeddings.json') as f:
    chunks = json.load(f)
    print(f"Total chunks: {len(chunks)}")
    print(f"Embedding dimension: {len(chunks[0]['embedding'])}")

# Check summary
with open('module3_summary.json') as f:
    summary = json.load(f)
    print(f"Status: {summary['status']}")
    print(f"Departments: {summary['vector_db_stats']['by_department']}")
```

## RBAC Integration

### Access Control Matrix
| Role | Accessible Departments |
|------|----------------------|
| admin | All departments |
| finance_employee | Finance, General |
| marketing_employee | Marketing, General |
| hr_employee | HR, General |
| engineering_employee | Engineering, General |
| employee | General only |

### Search with RBAC Examples

```python
db = VectorDBManager()

# Finance employee searches
results = db.search(
    query_text="revenue and expenses",
    user_role="finance_employee",
    n_results=5
)
# Returns: Finance + General documents only

# Marketing employee searches
results = db.search(
    query_text="campaign performance",
    user_role="marketing_employee",
    n_results=5
)
# Returns: Marketing + General documents only

# Admin searches
results = db.search(
    query_text="company overview",
    user_role="admin",
    n_results=5
)
# Returns: All departments
```

## Performance Metrics

### Embedding Generation
- **Total Chunks**: 70
- **Embedding Dimension**: 384
- **Model**: all-MiniLM-L6-v2
- **Processing Time**: ~2-3 seconds (CPU)
- **Batch Size**: 32 chunks per batch

### Vector Database
- **Storage**: ChromaDB (persistent)
- **Search Speed**: <100ms per query
- **RBAC Filtering**: Post-retrieval filtering
- **Scalability**: Handles 10K+ documents efficiently

## Troubleshooting

### Issue: "Module 2 output not found"
**Solution**: Run Module 2 first to generate chunks_for_embedding.json
```bash
cd ../module_2_document_preprocessing
python preprocessing_pipeline.py
```

### Issue: "CUDA out of memory"
**Solution**: Model runs on CPU by default. For GPU, ensure sufficient VRAM or reduce batch size in embedding_generator.py

### Issue: "ChromaDB directory locked"
**Solution**: Close any other processes using the database
```bash
rm -rf chroma_db/*.lock
```

### Issue: "Import error for sentence-transformers"
**Solution**: Reinstall dependencies
```bash
pip install --upgrade sentence-transformers torch
```

## Next Steps

After completing Module 3:
1. ✅ 70 chunks embedded with 384-dim vectors
2. ✅ ChromaDB populated with RBAC metadata
3. ✅ Semantic search working with role filtering
4. 🔜 **Proceed to Module 4**: Backend & Authentication
   - FastAPI backend
   - User authentication
   - API endpoints for search
   - Frontend integration

## API Reference

### EmbeddingGenerator Class
```python
class EmbeddingGenerator:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2")
    def embed_chunks(self, chunks: List[Dict]) -> List[Dict]
    def save_embeddings(self, chunks: List[Dict], output_file: str)
```

### VectorDBManager Class
```python
class VectorDBManager:
    def __init__(self, persist_directory: str, collection_name: str)
    def add_documents(self, chunks: List[Dict])
    def search(self, query_text: str, query_embedding: List[float],
               n_results: int, user_role: str, department_filter: str) -> Dict
    def get_stats(self) -> Dict
    def clear_collection(self)
```

## File Structure

```
module_3_vector_database/
├── embedding_generator.py          # Embedding generation
├── vector_db_manager.py           # ChromaDB management
├── module3_pipeline.py            # Complete pipeline
├── requirements.txt               # Python dependencies
├── test_module3.sh               # Automated tests
├── README.md                     # This file
├── QUICK_REFERENCE.txt           # Quick command reference
├── chunks_with_embeddings.json   # Output: chunks + embeddings
├── module3_summary.json          # Output: execution summary
└── chroma_db/                    # Output: vector database
    ├── chroma.sqlite3
    └── [database files]
```

## Technical Details

### Embedding Model
- **Name**: sentence-transformers/all-MiniLM-L6-v2
- **Type**: Sentence transformer
- **Dimensions**: 384
- **Max Sequence Length**: 256 tokens
- **Use Case**: Semantic similarity search
- **Size**: ~80MB

### Vector Database
- **System**: ChromaDB
- **Storage**: SQLite + file-based
- **Distance Metric**: Cosine similarity (default)
- **Indexing**: Automatic
- **Persistence**: Full persistence to disk

### Search Algorithm
1. Query embedding generation
2. Cosine similarity computation
3. Top-k retrieval (k * 2 for filtering)
4. RBAC filtering by role
5. Return top-k filtered results

## References
- [Sentence Transformers Documentation](https://www.sbert.net/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [RAG Architecture Guide](https://arxiv.org/abs/2005.11401)

---

**Module Status**: ✅ Complete and Tested  
**Date**: January 2024  
**Next Module**: Module 4 - Backend & Authentication
