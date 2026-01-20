# ===== api/hf_client.py =====

import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load .env
load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")

if not HF_API_TOKEN:
    raise RuntimeError("❌ HF_API_TOKEN is NOT set in environment variables!")

print("✅ HF Client Initialized")
print("🧠 Model:", HF_MODEL)

# Use official Hugging Face Inference Client (correct approach)
client = InferenceClient(
    model=HF_MODEL,
    token=HF_API_TOKEN
)

def call_hf_model(prompt: str) -> str:
    """
    Calls Hugging Face using chat_completion (correct for Mistral).
    Accepts a FULL RAG prompt from orchestrator.
    Returns clean generated text.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful RAG assistant. "
                "Answer strictly based on the provided context. "
                "Be clear, structured, and human-readable."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    try:
        response = client.chat_completion(
            messages=messages,
            max_tokens=400,
            temperature=0.2
        )
    except Exception as e:
        return f"LLM request failed: {str(e)}"

    # Extract text safely
    try:
        answer = response.choices[0].message["content"]
        return answer.strip()
    except Exception:
        return f"Unexpected HF response: {response}"
