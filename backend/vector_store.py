import os
import joblib
import chromadb
from sklearn.feature_extraction.text import TfidfVectorizer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "chroma_db")
MODEL_PATH = os.path.join(BASE_DIR, "tfidf_model.joblib")

COLLECTION_NAME = "company_docs_v2"

client = chromadb.PersistentClient(path=DB_DIR)
collection = client.get_or_create_collection(name=COLLECTION_NAME)

# Load or create TF-IDF model
if os.path.exists(MODEL_PATH):
    print("📦 Loaded existing TF-IDF model")
    vectorizer = joblib.load(MODEL_PATH)
else:
    vectorizer = TfidfVectorizer(stop_words="english")

def fit_vectorizer(texts):
    global vectorizer
    vectorizer.fit(texts)
    joblib.dump(vectorizer, MODEL_PATH)
    print("💾 Vectorizer saved to disk")

def embed(text):
    return vectorizer.transform([text]).toarray()[0].tolist()

def search_docs(query, role):
    query_emb = embed(query)

    if role == "admin":
        return collection.query(
            query_embeddings=[query_emb],
            n_results=3
        )

    return collection.query(
        query_embeddings=[query_emb],
        n_results=3,
        where={"role": {"$eq": role}}
    )

def persist_db():
    pass
