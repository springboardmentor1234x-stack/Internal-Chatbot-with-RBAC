import tiktoken
from typing import List, Dict, Any


def count_tokens(text: str, model="gpt-3.5-turbo"):
    """Count tokens in text for a specific model."""
    try:
        # Load the encoding for a specific model
        encoding = tiktoken.encoding_for_model(model)
        # Convert text to tokens
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        # Fallback: rough estimation (1 token ≈ 4 characters)
        return len(text) // 4


def format_chat_response(
    username: str, role: str, message: str, sources: List[str]
) -> Dict[str, Any]:
    """Format chat response with user info and sources."""
    return {
        "user": {"username": username, "role": role},
        "response": message,
        "sources": sources,
        "timestamp": (
            tiktoken.encoding_for_model("gpt-3.5-turbo").name
            if hasattr(tiktoken, "encoding_for_model")
            else "unknown"
        ),
        "token_count": count_tokens(message),
    }


# Test the token counting
if __name__ == "__main__":
    text = "Hello, how are you today?"
    print(f"Token count: {count_tokens(text)}")
