import re
from collections import defaultdict

class FinSolveRAGPipeline:
    def __init__(self, user_role):
        self.user_role = user_role
        # Step 1: RBAC Role Expansion (Inheritance)
        # Roles inherit permissions from lower levels
        self.role_hierarchy = {
            "Intern": ["Public", "General_HR"],
            "Financial_Analyst": ["Public", "General_HR", "Financial_Data"],
            "HR_Manager": ["Public", "General_HR", "HR_Sensitive"],
            "Engineering_Lead": ["Public", "General_HR", "Tech_Architecture"],
            "Cross_Dept_Manager": ["Public", "General_HR", "HR_Sensitive", "Tech_Architecture", "Financial_Data"]
        }
        self.allowed_scopes = self.role_hierarchy.get(user_role, ["Public"])

    def normalize_and_expand(self, query):
        """
        Step 2: Query Normalization & Variance Generation.
        Lowercases, strips, and generates multiple query perspectives.
        """
        normalized = query.lower().strip()
        variances = [
            normalized,
            f"technical details regarding {normalized}",
            f"policies and procedures for {normalized}",
            f"implementation of {normalized}"
        ]
        return variances

    def rbac_filter(self, candidates):
        """Step 3: RBAC Filtering of Chunks based on user inheritance."""
        filtered = []
        for chunk in candidates:
            # Check if chunk's required scope is in user's allowed scopes
            if chunk['scope'] in self.allowed_scopes:
                chunk['accessible'] = "GRANTED"
                filtered.append(chunk)
            else:
                chunk['accessible'] = "DENIED"
        return filtered

    def deduplicate_and_merge(self, results_list, k_constant=60):
        """Step 4: Reciprocal Rank Fusion (RRF) for merging results from multiple queries."""
        rrf_scores = defaultdict(float)
        chunk_metadata = {}

        for query_results in results_list:
            for rank, chunk in enumerate(query_results, start=1):
                chunk_id = chunk['chunk_id']
                # RRF Formula: 1 / (k + rank)
                rrf_scores[chunk_id] += 1.0 / (k_constant + rank)
                chunk_metadata[chunk_id] = chunk

        # Sort by RRF score descending
        sorted_ids = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return [chunk_metadata[cid] for cid, score in sorted_ids]

    def run_pipeline(self, user_query, top_k=5, threshold=0.7):
        """Main execution flow for the RAG Pipeline."""
        print(f"\n--- Executing Pipeline for Role: {self.user_role} ---")
        print(f"Query: '{user_query}'")

        # 1. Normalization & Variance
        queries = self.normalize_and_expand(user_query)

        all_retrieved = []
        for q in queries:
            # 2. Candidate Retrieval (Simulated Vector Search)
            raw_candidates = self.mock_retrieval(q)
            # 3. RBAC Filtering
            accessible_candidates = self.rbac_filter(raw_candidates)
            all_retrieved.append(accessible_candidates)

        # 4. Merging & Ranking (RRF)
        merged_results = self.deduplicate_and_merge(all_retrieved)

        # 5. Thresholding & Final Filter
        # Only return items where Access is GRANTED and Score is above threshold
        final_output = [
            r for r in merged_results 
            if r['score'] >= threshold and r['accessible'] == "GRANTED"
        ]

        return final_output[:top_k]

    def mock_retrieval(self, query):
        """Mock data representing chunks from Handbook and Engineering docs."""
        return [
            {"chunk_id": "HB-12", "doc_id": "employee_handbook.md", "scope": "General_HR", "score": 0.88},
            {"chunk_id": "ENG-42", "doc_id": "engineering_master_doc.md", "scope": "Tech_Architecture", "score": 0.91},
            {"chunk_id": "FIN-05", "doc_id": "quarterly_financial.md", "score": 0.85, "scope": "Financial_Data"},
            {"chunk_id": "HR-99", "doc_id": "hr_data.csv", "scope": "HR_Sensitive", "score": 0.95}
        ]

# --- Testing the Pipeline ---
if __name__ == "__main__":
    test_cases = [
        ("HR_Manager", "What is the exit policy?"),
        ("Intern", "What are the server specs?"),
        ("Financial_Analyst", "Q4 Revenue details"),
        ("Engineering_Lead", "How do we handle OAuth?"),
        ("Cross_Dept_Manager", "System architecture and payroll")
    ]

    for role, query in test_cases:
        pipeline = FinSolveRAGPipeline(role)
        results = pipeline.run_pipeline(query)

        print(f"Inheritance Scopes: {pipeline.allowed_scopes}")
        if not results:
            print(" >> No accessible results found for this query/role.")
        for res in results:
            print(f" >> [ID: {res['chunk_id']}] Doc: {res['doc_id']} | Access: {res['accessible']} | Score: {res['score']}")
        print("-" * 60)