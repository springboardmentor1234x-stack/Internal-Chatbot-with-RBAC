#!/usr/bin/env python3
"""
Debug script to check chunk analysis functionality
"""

import requests
import json

def test_chunk_analysis():
    """Test if chunk analysis is working properly"""
    print("🔍 Debugging Chunk Analysis...")
    
    # Login as admin
    login_response = requests.post(
        "http://127.0.0.1:8000/auth/login",
        data={"username": "admin", "password": "password123"},
        timeout=10
    )
    
    if login_response.status_code != 200:
        print("❌ Could not login")
        return
    
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test chat with detailed logging
    query = "What is our company policy?"
    print(f"📝 Testing query: {query}")
    
    chat_response = requests.post(
        "http://127.0.0.1:8000/api/v1/chat",
        json={"query": query},
        headers=headers,
        timeout=30
    )
    
    if chat_response.status_code == 200:
        data = chat_response.json()
        
        print("\n📊 Response Analysis:")
        print(f"✅ Response: {len(data.get('response', ''))} characters")
        print(f"📄 Sources: {len(data.get('sources', []))} documents")
        print(f"📈 Accuracy: {data.get('accuracy_score', 0):.1f}%")
        
        # Check chunk details
        chunk_details = data.get("chunk_details", [])
        print(f"🔍 Chunk Details: {len(chunk_details)} documents with chunks")
        
        if chunk_details:
            for i, chunk_info in enumerate(chunk_details, 1):
                doc_name = chunk_info.get("document_name", "Unknown")
                chunks = chunk_info.get("chunks", [])
                print(f"   📋 Document {i}: {doc_name}")
                print(f"      🔢 Chunks: {len(chunks)}")
                
                if chunks:
                    for j, chunk in enumerate(chunks[:2], 1):  # Show first 2 chunks
                        chunk_id = chunk.get("chunk_id", "N/A")
                        chunk_type = chunk.get("type", "N/A")
                        score = chunk.get("score", 0)
                        word_count = chunk.get("word_count", 0)
                        print(f"         🧩 Chunk {j}: {chunk_id}")
                        print(f"            Type: {chunk_type}, Score: {score:.3f}, Words: {word_count}")
        else:
            print("⚠️  No chunk details found in response")
            
        # Check citations
        citations = data.get("citations", [])
        print(f"📖 Citations: {len(citations)} found")
        
        if citations:
            for i, citation in enumerate(citations, 1):
                print(f"   📚 Citation {i}: {citation[:100]}...")
        
        # Print full response structure (keys only)
        print(f"\n🔑 Response Keys: {list(data.keys())}")
        
        # Save detailed response for analysis
        with open("debug_response.json", "w") as f:
            json.dump(data, f, indent=2)
        print("💾 Full response saved to debug_response.json")
        
    else:
        print(f"❌ Chat request failed: {chat_response.status_code}")
        print(f"Response: {chat_response.text}")

if __name__ == "__main__":
    test_chunk_analysis()