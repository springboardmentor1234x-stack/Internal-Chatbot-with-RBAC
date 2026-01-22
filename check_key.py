import os
from dotenv import load_dotenv

load_dotenv(override=True)

key = os.getenv("GEMINI_API_KEY")
print("KEY =", key)
