"""
Metadata Tagger - Assign role-based metadata to chunks
Tags chunks with department, accessible roles, permissions
"""

import json
from pathlib import Path
from typing import Dict, List, Any


class MetadataTagger:
    """Add role-based metadata to document chunks"""
    
    def __init__(self, role_mapping_file: str = None):
        """
        Initialize tagger with role mappings
        
        Args:
            role_mapping_file: Path to role_document_mapping.json
        """
        if role_mapping_file and Path(role_mapping_file).exists():
            with open(role_mapping_file, 'r') as f:
                self.role_mapping = json.load(f)
        else:
            # Default role mapping
            self.role_mapping = self._create_default_mapping()
        
        # Create department to roles mapping
        self.dept_to_roles = self._build_dept_to_roles()
    
    def _create_default_mapping(self) -> Dict[str, Any]:
        """Create default role mapping"""
        return {
            "admin": {
                "departments": ["Finance", "Marketing", "HR", "Engineering", "General"],
                "permissions": ["read", "write", "delete", "admin"]
            },
            "c_level": {
                "departments": ["Finance", "Marketing", "HR", "Engineering", "General"],
                "permissions": ["read"]
            },
            "finance_manager": {
                "departments": ["Finance", "General"],
                "permissions": ["read", "write", "delete"]
            },
            "finance_employee": {
                "departments": ["Finance", "General"],
                "permissions": ["read"]
            },
            "marketing_manager": {
                "departments": ["Marketing", "General"],
                "permissions": ["read", "write", "delete"]
            },
            "marketing_employee": {
                "departments": ["Marketing", "General"],
                "permissions": ["read"]
            },
            "hr_manager": {
                "departments": ["HR", "General"],
                "permissions": ["read", "write", "delete"]
            },
            "hr_employee": {
                "departments": ["HR", "General"],
                "permissions": ["read"]
            },
            "engineering_manager": {
                "departments": ["Engineering", "General"],
                "permissions": ["read", "write", "delete"]
            },
            "engineering_employee": {
                "departments": ["Engineering", "General"],
                "permissions": ["read"]
            },
            "employee": {
                "departments": ["General"],
                "permissions": ["read"]
            }
        }
    
    def _build_dept_to_roles(self) -> Dict[str, List[str]]:
        """
        Build mapping of department to accessible roles
        
        Returns:
            Dict mapping department name to list of roles that can access it
        """
        dept_to_roles = {}
        
        for role, config in self.role_mapping.items():
            for dept in config["departments"]:
                if dept not in dept_to_roles:
                    dept_to_roles[dept] = []
                dept_to_roles[dept].append(role)
        
        return dept_to_roles
    
    def get_accessible_roles(self, department: str) -> List[str]:
        """
        Get list of roles that can access a department
        
        Args:
            department: Department name
        
        Returns:
            List of role names
        """
        return self.dept_to_roles.get(department, [])
    
    def add_metadata(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add role-based metadata to a chunk
        
        Args:
            chunk: Chunk dict
        
        Returns:
            Chunk with added metadata
        """
        department = chunk.get('department', 'General')
        
        # Get accessible roles for this department
        accessible_roles = self.get_accessible_roles(department)
        
        # Add metadata
        chunk['metadata'] = {
            'department': department,
            'accessible_roles': accessible_roles,
            'source_file': chunk.get('source_document', ''),
            'chunk_id': chunk.get('chunk_id', ''),
            'chunk_index': chunk.get('chunk_index', 0),
            'document_title': chunk.get('document_title', ''),
        }
        
        # Add RBAC filter hint for vector DB
        chunk['rbac_filter'] = {
            'department': department,
            'allowed_roles': accessible_roles
        }
        
        return chunk
    
    def tag_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add metadata to all chunks
        
        Args:
            chunks: List of chunk dicts
        
        Returns:
            List of chunks with metadata
        """
        tagged_chunks = []
        
        for chunk in chunks:
            tagged_chunk = self.add_metadata(chunk)
            tagged_chunks.append(tagged_chunk)
        
        return tagged_chunks
    
    def get_metadata_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about metadata distribution
        """
        stats = {
            'total_chunks': len(chunks),
            'by_department': {},
            'by_role_access': {},
            'avg_roles_per_chunk': 0
        }
        
        role_counts = []
        
        for chunk in chunks:
            dept = chunk['metadata']['department']
            roles = chunk['metadata']['accessible_roles']
            
            # Count by department
            if dept not in stats['by_department']:
                stats['by_department'][dept] = 0
            stats['by_department'][dept] += 1
            
            # Count by role
            role_counts.append(len(roles))
            for role in roles:
                if role not in stats['by_role_access']:
                    stats['by_role_access'][role] = 0
                stats['by_role_access'][role] += 1
        
        # Calculate average
        if role_counts:
            stats['avg_roles_per_chunk'] = sum(role_counts) / len(role_counts)
        
        return stats


def main():
    """Test the metadata tagger"""
    print("=" * 60)
    print("METADATA TAGGER TEST")
    print("=" * 60)
    
    # Try to load role mapping from Module 1
    role_mapping_file = "../module_1_environment_setup/role_document_mapping.json"
    tagger = MetadataTagger(role_mapping_file)
    
    print(f"\n✓ Loaded role mapping for {len(tagger.role_mapping)} roles")
    print(f"✓ Department-to-role mapping created")
    
    # Test chunks
    test_chunks = [
        {
            'chunk_id': 'financial_summary.md_0',
            'text': 'Revenue grew by 25% in 2024...',
            'department': 'Finance',
            'source_document': 'financial_summary.md',
            'document_title': 'Financial Summary'
        },
        {
            'chunk_id': 'marketing_report.md_0',
            'text': 'Q4 marketing campaign results...',
            'department': 'Marketing',
            'source_document': 'marketing_report.md',
            'document_title': 'Marketing Report'
        },
        {
            'chunk_id': 'employee_handbook.md_0',
            'text': 'Company policies and procedures...',
            'department': 'General',
            'source_document': 'employee_handbook.md',
            'document_title': 'Employee Handbook'
        }
    ]
    
    # Tag chunks
    tagged = tagger.tag_chunks(test_chunks)
    
    print(f"\n📦 Tagged {len(tagged)} chunks:\n")
    
    for chunk in tagged:
        print(f"Chunk: {chunk['chunk_id']}")
        print(f"  Department: {chunk['metadata']['department']}")
        print(f"  Accessible by: {', '.join(chunk['metadata']['accessible_roles'])}")
        print(f"  Total roles: {len(chunk['metadata']['accessible_roles'])}")
        print()
    
    # Show stats
    stats = tagger.get_metadata_stats(tagged)
    print("📊 Metadata Statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  By department: {stats['by_department']}")
    print(f"  Avg roles per chunk: {stats['avg_roles_per_chunk']:.1f}")
    
    print("\n" + "=" * 60)
    print("✅ Metadata tagging complete")


if __name__ == "__main__":
    main()
