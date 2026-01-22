from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

print("🚀 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)

print("🚀 Loading model (one-time)...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    device_map="auto"
)

def generate_answer(question: str) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": question}
    ]

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(prompt, return_tensors="pt")

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150
        )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)
