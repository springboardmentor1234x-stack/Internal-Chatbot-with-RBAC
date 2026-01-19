from rag.orchestrator import run_rag_pipeline

# --------------------------------------------------
# Mock user (simulating logged-in user)
# --------------------------------------------------
test_user = {
    "sub": "test.user@company.com",
    "role": "intern"   # change this to intern / manager / admin to test RBAC
}

# --------------------------------------------------
# Test query
# --------------------------------------------------
query = "What is the company leave policy?"

# --------------------------------------------------
# Run RAG pipeline
# --------------------------------------------------
response = run_rag_pipeline(
    user=test_user,
    query=query,
    top_k=5
)

# --------------------------------------------------
# Print output
# --------------------------------------------------
print("\n===== RAG PIPELINE OUTPUT =====\n")
print("User:", response["user"])
print("Role:", response["role"])
print("Query:", response["query"])

print("\n--- Formatted Context ---\n")
print(response.get("formatted_context"))

print("\n--- Citations ---\n")
for c in response.get("citations", []):
    print(c)
