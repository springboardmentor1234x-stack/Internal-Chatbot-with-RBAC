# Module 2: Document Preprocessing & Metadata Tagging

## ✅ Status: COMPLETE

## What This Module Does

Processes all 10 documents from the Dataset and prepares them for vector embedding:
1. **Parses** markdown (.md) and CSV (.csv) files
2. **Cleans** text (normalize unicode, fix encoding, mask emails)
3. **Chunks** documents into 300-512 token segments with overlap
4. **Tags** each chunk with role-based metadata for RBAC

## Files Created

### Core Components
- `document_parser.py` - Parse .md and .csv files
- `text_cleaner.py` - Clean and normalize text
- `document_chunker.py` - Split into chunks (300-512 tokens)
- `metadata_tagger.py` - Add RBAC metadata
- `preprocessing_pipeline.py` - Orchestrates all steps

### Testing
- `test_module2.sh` - Automated test suite
- `requirements.txt` - Dependencies (tiktoken)

### Output Files (Generated)
- `processed_chunks.json` - All 70 chunks with full metadata
- `preprocessing_summary.json` - Statistics and summary
- `chunks_for_embedding.json` - Embedding-ready format

## Results

### Documents Processed: 10
- Marketing: 5 files → 16 chunks
- Finance: 2 files → 9 chunks
- HR: 1 file → 25 chunks
- Engineering: 1 file → 13 chunks
- General: 1 file → 7 chunks

### Total Chunks: 70
- Average size: 478 tokens
- Range: 25-512 tokens
- Average roles per chunk: 4.7

### Metadata Added
Each chunk includes:
- `chunk_id` - Unique identifier
- `text` - Cleaned content
- `token_count` - Size in tokens
- `department` - Source department
- `accessible_roles` - List of roles with access
- `rbac_filter` - For vector DB filtering

## Testing

### Quick Test
```bash
cd module_2_document_preprocessing
./test_module2.sh
```

Expected: **13/13 tests passed**

### Manual Test
```bash
# Run individual components
python document_parser.py
python text_cleaner.py
python document_chunker.py
python metadata_tagger.py

# Run complete pipeline
python preprocessing_pipeline.py

# View results
cat preprocessing_summary.json
```

## Key Features

### 1. Multi-Format Support
- Markdown with section extraction
- CSV with row-to-text conversion

### 2. Smart Chunking
- Token-aware splitting (uses tiktoken)
- Paragraph-based chunking when possible
- Overlap for context preservation

### 3. RBAC Metadata
- Department-based access control
- Role-to-chunk mapping
- Ready for vector DB filtering

### 4. Text Cleaning
- Unicode normalization
- Email masking for privacy
- Whitespace normalization
- Encoding fixes

## Output Format

Each chunk in `processed_chunks.json`:
```json
{
  "chunk_id": "financial_summary.md_0",
  "text": "Revenue grew by 25%...",
  "token_count": 456,
  "chunk_index": 0,
  "total_chunks": 4,
  "source_document": "financial_summary.md",
  "department": "Finance",
  "document_title": "Financial Summary",
  "metadata": {
    "department": "Finance",
    "accessible_roles": ["admin", "c_level", "finance_manager", "finance_employee"],
    "source_file": "financial_summary.md",
    "chunk_id": "financial_summary.md_0"
  },
  "rbac_filter": {
    "department": "Finance",
    "allowed_roles": ["admin", "c_level", "finance_manager", "finance_employee"]
  }
}
```

## Next Steps

Module 3 will:
- Generate embeddings for all 70 chunks
- Store in ChromaDB vector database
- Enable semantic search
- Implement RBAC filtering at retrieval time

## Dependencies

- tiktoken: Accurate token counting (OpenAI tokenizer)
- Standard library: json, re, csv, pathlib

Install: `pip install tiktoken`
