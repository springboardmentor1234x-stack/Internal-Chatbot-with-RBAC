import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")

print("HF_API_TOKEN:", HF_API_TOKEN)

# ✅ OFFICIAL CLIENT (correct usage for Mistral)
client = InferenceClient(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    token=HF_API_TOKEN
)

# ✅ Use conversational API instead of text_generation
messages = [
    {
        "role": "user",
        "content": "Hello, say hi!"
    }
]

response = client.chat_completion(
    messages=messages,
    max_tokens=100,
    temperature=0.2
)

print("\n=== RESPONSE ===\n")
print(response.choices[0].message["content"])
