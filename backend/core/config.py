#config.py
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY missing in .env")

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = str(BASE_DIR / "data")
CHROMA_DIR = str(BASE_DIR / "chroma_db")  # ✅ FIXED

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
) 