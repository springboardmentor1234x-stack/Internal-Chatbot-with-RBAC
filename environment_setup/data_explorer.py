"""
Data Exploration and Role Mapping Module
This module explores the company documents and creates role-to-document mappings
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd


class DataExplorer:
    """Explore company documents and create role mappings"""
    
    def __init__(self, base_path: str = "../Dataset"):
        self.base_path = Path(base_path)
        self.documents = []
        self.role_mapping = {}
        
    def explore_documents(self) -> Dict[str, Any]:
        """
        Explore all documents in the Dataset directory
        Returns summary of documents found
        """
        summary = {
            "total_documents": 0,
            "by_department": {},
            "file_types": {},
            "total_size_bytes": 0
        }
        
        # Iterate through department folders
        for dept_folder in self.base_path.iterdir():
            if dept_folder.is_dir():
                dept_name = dept_folder.name
                dept_files = []
                
                for file_path in dept_folder.iterdir():
                    if file_path.is_file():
                        file_info = {
                            "filename": file_path.name,
                            "path": str(file_path),
                            "size": file_path.stat().st_size,
                            "extension": file_path.suffix,
                            "department": dept_name
                        }
                        dept_files.append(file_info)
                        self.documents.append(file_info)
                        
                        # Update summary
                        summary["total_documents"] += 1
                        summary["total_size_bytes"] += file_info["size"]
                        
                        # Count file types
                        ext = file_path.suffix
                        summary["file_types"][ext] = summary["file_types"].get(ext, 0) + 1
                
                summary["by_department"][dept_name] = {
                    "count": len(dept_files),
                    "files": [f["filename"] for f in dept_files]
                }
        
        return summary
    
    def create_role_mapping(self) -> Dict[str, Dict[str, Any]]:
        """
        Create role-to-document mapping based on RBAC rules
        
        Role Hierarchy:
        - admin: Full access to all departments
        - c_level: Access to all departments
        - finance_manager: Finance + General
        - finance_employee: Finance + General
        - marketing_manager: Marketing + General
        - marketing_employee: Marketing + General
        - hr_manager: HR + General
        - hr_employee: HR + General
        - engineering_manager: Engineering + General
        - engineering_employee: Engineering + General
        - employee: General only
        """
        
        self.role_mapping = {
            "admin": {
                "departments": ["Finance", "Marketing", "HR", "Engineering", "General"],
                "permissions": ["read", "write", "delete", "admin"],
                "description": "Full system access"
            },
            "c_level": {
                "departments": ["Finance", "Marketing", "HR", "Engineering", "General"],
                "permissions": ["read"],
                "description": "C-Level executives - read access to all departments"
            },
            "finance_manager": {
                "departments": ["Finance", "General"],
                "permissions": ["read", "write", "delete"],
                "description": "Finance department manager"
            },
            "finance_employee": {
                "departments": ["Finance", "General"],
                "permissions": ["read"],
                "description": "Finance department employee"
            },
            "marketing_manager": {
                "departments": ["Marketing", "General"],
                "permissions": ["read", "write", "delete"],
                "description": "Marketing department manager"
            },
            "marketing_employee": {
                "departments": ["Marketing", "General"],
                "permissions": ["read"],
                "description": "Marketing department employee"
            },
            "hr_manager": {
                "departments": ["HR", "General"],
                "permissions": ["read", "write", "delete"],
                "description": "HR department manager"
            },
            "hr_employee": {
                "departments": ["HR", "General"],
                "permissions": ["read"],
                "description": "HR department employee"
            },
            "engineering_manager": {
                "departments": ["Engineering", "General"],
                "permissions": ["read", "write", "delete"],
                "description": "Engineering department manager"
            },
            "engineering_employee": {
                "departments": ["Engineering", "General"],
                "permissions": ["read"],
                "description": "Engineering department employee"
            },
            "employee": {
                "departments": ["General"],
                "permissions": ["read"],
                "description": "General employee - access to employee handbook only"
            }
        }
        
        return self.role_mapping
    
    def get_accessible_documents(self, role: str) -> List[Dict[str, Any]]:
        """
        Get list of documents accessible by a specific role
        """
        if role not in self.role_mapping:
            return []
        
        allowed_departments = self.role_mapping[role]["departments"]
        accessible_docs = [
            doc for doc in self.documents 
            if doc["department"] in allowed_departments
        ]
        
        return accessible_docs
    
    def generate_content_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of document content
        """
        content_summary = {}
        
        for doc in self.documents:
            dept = doc["department"]
            if dept not in content_summary:
                content_summary[dept] = {
                    "files": [],
                    "total_size": 0,
                    "file_count": 0
                }
            
            content_summary[dept]["files"].append({
                "name": doc["filename"],
                "size": doc["size"],
                "type": doc["extension"]
            })
            content_summary[dept]["total_size"] += doc["size"]
            content_summary[dept]["file_count"] += 1
        
        return content_summary
    
    def save_mappings(self, output_dir: str = "."):
        """
        Save role mappings and document summaries to JSON files
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save role mapping
        with open(output_path / "role_document_mapping.json", "w") as f:
            json.dump(self.role_mapping, f, indent=2)
        
        # Save document inventory
        doc_inventory = {
            "documents": self.documents,
            "summary": self.generate_content_summary()
        }
        with open(output_path / "document_inventory.json", "w") as f:
            json.dump(doc_inventory, f, indent=2)
        
        print(f"✅ Mappings saved to {output_path}")


def main():
    """Main execution function"""
    print("=" * 60)
    print("MODULE 1: DATA EXPLORATION & ROLE MAPPING")
    print("=" * 60)
    
    # Initialize explorer
    explorer = DataExplorer()
    
    # Explore documents
    print("\n📂 Exploring documents...")
    summary = explorer.explore_documents()
    
    print(f"\n📊 Document Summary:")
    print(f"   Total Documents: {summary['total_documents']}")
    print(f"   Total Size: {summary['total_size_bytes'] / 1024:.2f} KB")
    print(f"\n   By Department:")
    for dept, info in summary['by_department'].items():
        print(f"      {dept}: {info['count']} files")
        for filename in info['files']:
            print(f"         - {filename}")
    
    print(f"\n   File Types:")
    for ext, count in summary['file_types'].items():
        print(f"      {ext}: {count} files")
    
    # Create role mapping
    print("\n🔐 Creating role mappings...")
    role_mapping = explorer.create_role_mapping()
    
    print(f"\n📋 Role Mapping Created:")
    for role, config in role_mapping.items():
        print(f"\n   {role}:")
        print(f"      Departments: {', '.join(config['departments'])}")
        print(f"      Permissions: {', '.join(config['permissions'])}")
        print(f"      Description: {config['description']}")
    
    # Test access for different roles
    print("\n🧪 Testing Role-Based Access:")
    test_roles = ["finance_employee", "marketing_manager", "c_level", "employee"]
    for role in test_roles:
        accessible = explorer.get_accessible_documents(role)
        print(f"\n   {role} can access {len(accessible)} documents:")
        for doc in accessible[:3]:  # Show first 3
            print(f"      - {doc['filename']} ({doc['department']})")
        if len(accessible) > 3:
            print(f"      ... and {len(accessible) - 3} more")
    
    # Save mappings
    print("\n💾 Saving mappings...")
    explorer.save_mappings(".")
    
    print("\n✅ Module 1 Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
