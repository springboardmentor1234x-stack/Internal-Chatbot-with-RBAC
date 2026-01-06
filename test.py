import requests
from backend.config import Config
headers = {"Authorization": f"Bearer {Config.HF_API_TOKEN}", "Content-Type": "application/json"}
url = f"https://router.huggingface.co/models/{Config.HF_MODEL}"

payload = {
    "inputs": "Answer briefly: What is role-based access control?",
    "parameters": {
        "max_new_tokens": 50,
        "temperature": 0.3,
        "top_p": 0.9,
        "do_sample": False,
        "return_full_text": False
    }
}
try:
    response = requests.post(url, headers=headers, json=payload, timeout=30)

    print("HTTP Status Code:", response.status_code)
    print("Response Headers:", response.headers)
    print("Raw Response Text:", repr(response.text))

    # ---- SAFE JSON HANDLING ----
    if not response.text.strip():
        print("❌ ERROR: Empty response body from Hugging Face")
    
    elif response.headers.get("content-type", "").startswith("application/json"):
        try:
            data = response.json()
            print("✅ Parsed JSON Response:")
            print(data)
        except ValueError as e:
            print("❌ JSON parsing failed:", str(e))
    
    else:
        print("❌ Non-JSON response received")
        print(response.text)

except requests.exceptions.Timeout:
    print("❌ ERROR: Request timed out")

except requests.exceptions.RequestException as e:
    print("❌ HTTP Request failed:", str(e))
