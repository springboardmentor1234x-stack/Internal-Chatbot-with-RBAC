import tiktoken

def count_tokens(text: str, model="gpt-3.5-turbo"):
    # Load the encoding for a specific model
    encoding = tiktoken.encoding_for_model(model)
    # Convert text to tokens
    tokens = encoding.encode(text)
    return len(tokens)

text = "Hello, how are you today?"
print(f"Token count: {count_tokens(text)}")