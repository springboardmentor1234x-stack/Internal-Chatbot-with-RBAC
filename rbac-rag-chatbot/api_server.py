import uvicorn
from dotenv import load_dotenv
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")

print(f"🔍 Loading .env from: {env_path}")
print(f"📁 .env exists? {os.path.exists(env_path)}")

load_dotenv(env_path)

print("✅ HF_API_TOKEN loaded as:", os.getenv("HF_API_TOKEN"))
print("✅ HF_MODEL loaded as:", os.getenv("HF_MODEL"))

from api.app import app


if __name__ == "__main__":
    uvicorn.run(
        "api.app:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )
