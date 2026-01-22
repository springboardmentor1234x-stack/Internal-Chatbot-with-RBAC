import os
import requests
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("❌ HF_TOKEN not found")
    exit()

API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

payload = {
    "model": "HuggingFaceH4/zephyr-7b-beta",
    "messages": [
        {"role": "user", "content": "Explain company leave policy in simple words."}
    ],
    "max_tokens": 200
}

response = requests.post(API_URL, headers=headers, json=payload)

print("STATUS CODE:", response.status_code)
print("RAW RESPONSE:\n", response.text)

try:
    data = response.json()
    print("\n✅ ANSWER:\n")
    print(data["choices"][0]["message"]["content"])
except Exception as e:
    print("❌ Could not parse response:", e)
