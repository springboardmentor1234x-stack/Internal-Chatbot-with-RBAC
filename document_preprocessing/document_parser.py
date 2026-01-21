"""
Document Parser - Parse markdown and CSV files
Handles .md and .csv files from the Dataset
"""

import re
import csv
from pathlib import Path
from typing import Dict, List, Any
import json


class DocumentParser:
    """Parse different document formats"""
    
    def __init__(self, dataset_path: str = "../Dataset"):
        self.dataset_path = Path(dataset_path)
        
    def parse_markdown(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse markdown file and extract structured content
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem
        
        # Extract sections
        sections = []
        section_pattern = r'^#+\s+(.+?)$'
        section_splits = re.split(section_pattern, content, flags=re.MULTILINE)
        
        # First part is content before first heading
        if section_splits[0].strip():
            sections.append({
                'heading': 'Introduction',
                'content': section_splits[0].strip()
            })
        
        # Process remaining sections (alternating heading, content)
        for i in range(1, len(section_splits), 2):
            if i + 1 < len(section_splits):
                sections.append({
                    'heading': section_splits[i].strip(),
                    'content': section_splits[i + 1].strip()
                })
        
        return {
            'title': title,
            'content': content,
            'sections': sections,
            'length': len(content),
            'format': 'markdown'
        }
    
    def parse_csv(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse CSV file and convert to structured text
        """
        rows = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            for row in reader:
                rows.append(row)
        
        # Convert CSV to readable text format
        text_content = []
        for row in rows:
            row_text = []
            for key, value in row.items():
                row_text.append(f"{key}: {value}")
            text_content.append(" | ".join(row_text))
        
        content = "\n".join(text_content)
        
        return {
            'title': file_path.stem,
            'content': content,
            'headers': headers,
            'row_count': len(rows),
            'format': 'csv',
            'length': len(content)
        }
    
    def parse_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse any supported document format
        """
        if file_path.suffix == '.md':
            return self.parse_markdown(file_path)
        elif file_path.suffix == '.csv':
            return self.parse_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def parse_all_documents(self) -> List[Dict[str, Any]]:
        """
        Parse all documents in the Dataset directory
        """
        parsed_docs = []
        
        for dept_folder in self.dataset_path.iterdir():
            if dept_folder.is_dir():
                dept_name = dept_folder.name
                
                for file_path in dept_folder.iterdir():
                    if file_path.is_file() and file_path.suffix in ['.md', '.csv']:
                        try:
                            parsed = self.parse_document(file_path)
                            parsed['department'] = dept_name
                            parsed['filename'] = file_path.name
                            parsed['filepath'] = str(file_path)
                            parsed_docs.append(parsed)
                            print(f"✓ Parsed: {file_path.name} ({dept_name})")
                        except Exception as e:
                            print(f"✗ Error parsing {file_path.name}: {e}")
        
        return parsed_docs


def main():
    """Test the document parser"""
    print("=" * 60)
    print("DOCUMENT PARSER TEST")
    print("=" * 60)
    
    parser = DocumentParser()
    docs = parser.parse_all_documents()
    
    print(f"\n📊 Parsed {len(docs)} documents\n")
    
    for doc in docs:
        print(f"📄 {doc['filename']} ({doc['department']})")
        print(f"   Format: {doc['format']}")
        print(f"   Length: {doc['length']:,} characters")
        if doc['format'] == 'markdown' and doc.get('sections'):
            print(f"   Sections: {len(doc['sections'])}")
        if doc['format'] == 'csv':
            print(f"   Rows: {doc['row_count']}")
        print()
    
    # Save parsed documents
    output_file = "parsed_documents.json"
    with open(output_file, 'w') as f:
        json.dump(docs, f, indent=2)
    print(f"✅ Saved to {output_file}")


if __name__ == "__main__":
    main()
