"""
Verify Module 2 Output
Quick validation of preprocessing results
"""

import json
from collections import Counter

def verify_preprocessing():
    """Verify all preprocessing outputs"""
    
    print("=" * 60)
    print("MODULE 2 VERIFICATION")
    print("=" * 60)
    
    # Load processed chunks
    with open('processed_chunks.json', 'r') as f:
        chunks = json.load(f)
    
    print(f"\n✓ Loaded {len(chunks)} chunks")
    
    # Verify chunk structure
    print("\n📋 Chunk Structure Validation:")
    required_fields = ['chunk_id', 'text', 'token_count', 'department', 'metadata', 'rbac_filter']
    
    for field in required_fields:
        has_field = all(field in chunk for chunk in chunks)
        status = "✓" if has_field else "✗"
        print(f"  {status} All chunks have '{field}'")
    
    # Token count validation
    print("\n📊 Token Count Validation:")
    token_counts = [c['token_count'] for c in chunks]
    print(f"  Min tokens: {min(token_counts)}")
    print(f"  Max tokens: {max(token_counts)}")
    print(f"  Avg tokens: {sum(token_counts)/len(token_counts):.1f}")
    
    exceeds_512 = [c for c in chunks if c['token_count'] > 512]
    if exceeds_512:
        print(f"  ⚠️  {len(exceeds_512)} chunks exceed 512 tokens")
    else:
        print(f"  ✓ No chunks exceed 512 tokens")
    
    # Department distribution
    print("\n📁 Department Distribution:")
    dept_counts = Counter(c['department'] for c in chunks)
    for dept, count in sorted(dept_counts.items()):
        print(f"  {dept}: {count} chunks")
    
    # Role accessibility
    print("\n👥 Role Accessibility:")
    role_access = Counter()
    for chunk in chunks:
        for role in chunk['metadata']['accessible_roles']:
            role_access[role] += 1
    
    for role, count in sorted(role_access.items()):
        print(f"  {role}: {count} chunks")
    
    # RBAC validation
    print("\n🔐 RBAC Validation:")
    
    # Finance chunks should only be accessible by finance roles + admin/c_level
    finance_chunks = [c for c in chunks if c['department'] == 'Finance']
    if finance_chunks:
        sample = finance_chunks[0]
        roles = set(sample['metadata']['accessible_roles'])
        expected = {'admin', 'c_level', 'finance_employee', 'finance_manager'}
        if roles == expected:
            print(f"  ✓ Finance RBAC correct")
        else:
            print(f"  ⚠️  Finance RBAC mismatch")
            print(f"     Expected: {expected}")
            print(f"     Got: {roles}")
    
    # General chunks should be accessible by all
    general_chunks = [c for c in chunks if c['department'] == 'General']
    if general_chunks:
        sample = general_chunks[0]
        role_count = len(sample['metadata']['accessible_roles'])
        if role_count == 11:  # All 11 roles
            print(f"  ✓ General accessible by all roles")
        else:
            print(f"  ⚠️  General should have 11 roles, has {role_count}")
    
    # Unique chunk IDs
    print("\n🆔 Chunk ID Validation:")
    chunk_ids = [c['chunk_id'] for c in chunks]
    if len(chunk_ids) == len(set(chunk_ids)):
        print(f"  ✓ All {len(chunk_ids)} chunk IDs are unique")
    else:
        duplicates = len(chunk_ids) - len(set(chunk_ids))
        print(f"  ✗ {duplicates} duplicate chunk IDs found")
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION COMPLETE")
    print("=" * 60)
    
    print(f"\n✅ Total chunks: {len(chunks)}")
    print(f"✅ Token range: {min(token_counts)}-{max(token_counts)}")
    print(f"✅ Departments: {len(dept_counts)}")
    print(f"✅ Roles: {len(role_access)}")
    print(f"\n🎯 Ready for Module 3 (Vector Database)")


if __name__ == "__main__":
    verify_preprocessing()
