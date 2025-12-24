import json, os
import numpy as np
import chromadb
from RAGPipeline.RAGPipeline import RAGPipeline
from RAGPipeline.QueryNormalizer import QueryNormalizer
from RAGPipeline.VectorRetriever import VectorRetriever
from RAGPipeline.RBACEngine import RBACEngine
from RAGPipeline.ReRanker import ReRanker

class RAGSystem:
    def __init__(self, config_path="Internal-Chatbot-with-RBAC-Project/config.py"):
        self.config = self._load_config(config_path)
        self.chunks = self._load_json(self.config["chunks_file"])
        self.metadata = self._load_json(self.config["metadata_file"])
        self.abbreviations = self._load_json(self.config["abbreviations_file"])
        self.rbac_config = self._load_json(self.config["rbac_permissions_file"])
        self.embeddings = np.load(self.config["embeddings_file"])
        self.vector_db_path = self.config["vector_db"]

        # Initialize ChromaDB
        self.chroma_client = self.load_vector_db(self.vector_db_path)
        
        # Initialize pipeline components
        self.pipeline = None
        
        print("✓ RAG System initialized successfully")
    
    def _load_config(self, config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # Return default configuration
            return {
                "chunks_file": "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/Chunking/all_chunks.json",
                "metadata_file": "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/Chunking/all_metadata.json",
                "embeddings_file": "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/Embeddings/chunk_embeddings.npy",
                "abbreviations_file": "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/RAGPipeline/ABBREVATIONS.json",
                "rbac_permissions_file": "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/RAGPipeline/rbac_permissions.json",
                "vector_db": "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC-Project/VectorDB",
                "similarity_threshold": 0.30,
                "top_k": 3
            }
    
    def _load_json(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load {filepath}: {str(e)}")
    
    def load_vector_db(self, db_path):
        if not os.path.exists(db_path):
            raise FileNotFoundError(
                f"Vector DB directory not found: {db_path}"
            )

        client = chromadb.PersistentClient(
            path=db_path
        )

        print(f"Vector DB loaded from: {db_path}")
        
        return client
    
    def create_pipeline(self, user_roles, similarity_threshold=None):
        if similarity_threshold is None:
            similarity_threshold = self.config["similarity_threshold"]
        
        # Initialize components
        normalizer = QueryNormalizer(self.abbreviations)
        retriever = VectorRetriever(
            self.chroma_client,
            self.chunks,
            self.metadata,
            self.embeddings,
            self.config.get("embedding_model_name", "sentence-transformers/all-MiniLM-L6-v2")
        )
        rbac = RBACEngine(
            user_roles=user_roles,
            rbac_config=self.rbac_config
        )
        ranker = ReRanker(similarity_threshold=similarity_threshold)
        
        self.pipeline = RAGPipeline(
            normalizer=normalizer,
            retriever=retriever,
            rbac=rbac,
            ranker=ranker
        )
        
        print(f"✓ Pipeline created for roles: {user_roles}")
        return self.pipeline
    
    def query(self, raw_query, department=None, top_k=None, user_roles=None):
        if top_k is None:
            top_k = self.config["top_k"]
        
        if user_roles and self.pipeline is None:
            self.create_pipeline(user_roles)
        
        if self.pipeline is None:
            raise RuntimeError("Pipeline not initialized. Call create_pipeline() first.")
        
        return self.pipeline.run(
            raw_query=raw_query,
            # department=department,
            top_k=top_k
        )
    
    def display_results(self, results):
        if not results:
            print("\nNo results found matching your query and access permissions.")
            return
        
        print(f"\n{'='*80}")
        print(f"QUERY RESULTS ({len(results)} matches)")
        print(f"{'='*80}\n")
        
        for i, result in enumerate(results, 1):
            print(f"[{i}] Similarity: {result['similarity']:.4f} | Chunk: {result['id']}")
            print(f"    Department: {result['metadata']['department']}")
            print(f"    Source: {result['metadata']['source_document']}")
            print(f"    Security: {result['metadata']['security_level']}")
            
            # Show snippet of content
            content = result.get('content', '')[:200]
            print(f"    Content: {content}...")
            print()


def main():
    print("\n" + "="*80)
    print("RAG PIPELINE WITH RBAC")
    print("="*80 + "\n")
    
    # Initialize system
    rag_system = RAGSystem()
    
    # Test scenarios
    test_cases = [
        # {
        #     "query": "lead-conversion !!! anomaly?? detect :: marketing q1 to   q2",
        #     "roles": ["Security Officer", "Marketing Analyst"]
        # },
        # {
        #     "query": "regional / campaign $$ spend  compliance-review  quarter1–Q2",
        #     "roles": ["CMO", "Compliance Officer"]
        # },
        {
            "query": "company leave policies and internal guidelines Q2-Q3",
            "roles": ["Intern"]
        },
        # {
        #     "query": "Q1 revenue growth analysis and cost breakdown",
        #     "roles": ["Finance Analyst"]
        # },
        # {
        #     "query": "salary revision process and appraisal cycle details",
        #     "roles": ["HR Executive"]
        # },
        # {
        #     "query": "department-wise performance summary Q2",
        #     "roles": ["Manager"]
        # },
        # {
        #     "query": "overall company strategy, revenue, hiring, and security overview Q1-Q4",
        #     "roles": ["Admin"]
        # },
        # {
        #     "query": "data security protocols and compliance measures",
        #     "roles": ["Backend Developer", "Security Officer"]
        # },
    ]
    
    # Run test cases
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─'*80}")
        print(f"TEST CASE {i}")
        print(f"Query: \"{test['query']}\"")
        print(f"Roles: {test['roles']}")
        print(f"{'─'*80}")
        
        try:
            results = rag_system.query(
                raw_query=test['query'],
                # department=test['department'],
                user_roles=test['roles'],
                top_k=3
            )
            rag_system.display_results(results)
        except Exception as e:
            print(f"\nError: {str(e)}\n")
    
    # # Interactive mode
    # print("\n" + "="*80)
    # print("INTERACTIVE MODE")
    # print("="*80 + "\n")
    # print("Available roles: CMO, HR Manager, Finance Manager, Backend Developer, etc.")
    # print("Type 'exit' to quit\n")
    
    # while True:
    #     try:
    #         query = input("\nEnter your query: ").strip()
    #         if query.lower() == 'exit':
    #             break
            
    #         roles_input = input("Enter your role(s) (comma-separated): ").strip()
    #         roles = [r.strip() for r in roles_input.split(",")]
            
    #         dept_input = input("Enter department (optional, press Enter to skip): ").strip()
    #         dept = dept_input if dept_input else None
            
    #         results = rag_system.query(
    #             raw_query=query,
    #             department=dept,
    #             user_roles=roles,
    #             top_k=3
    #         )
    #         rag_system.display_results(results)
            
    #     except KeyboardInterrupt:
    #         print("\n\nExiting...")
    #         break
    #     except Exception as e:
    #         print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()