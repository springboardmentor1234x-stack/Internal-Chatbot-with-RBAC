from rag.llm import summarize_large_text, generate_answer_from_summaries

# -----------------------------
# Example text for testing
# -----------------------------
chunk1 = "The company revenue in 2024 grew by 15% compared to 2023."
chunk2 = "Profit margins also improved by 5% due to cost optimization."
chunk3 = "Customer satisfaction scores increased by 10 points in 2024."
chunk4 = "Expansion into new markets contributed to revenue growth."

# Simulate a large document by joining multiple chunks
large_text = "\n".join([chunk1, chunk2, chunk3, chunk4])

# -----------------------------
# Summarize large text
# -----------------------------
chunk_summaries, final_summary = summarize_large_text(
    large_text,
    chunk_size=100,  # small chunk size for testing splitting logic
    hierarchical=True
)

print("Per-chunk summaries:")
for i, s in enumerate(chunk_summaries, 1):
    print(f"{i}. {s}")

print("\nFinal hierarchical summary:")
print(final_summary)

# -----------------------------
# Generate answer from hierarchical summary
# -----------------------------
question = "What was the overall performance of the company in 2024?"
answer = generate_answer_from_summaries(
    summaries=[final_summary],  # feed as list
    user_query=question
)

print("\nAnswer to the question:")
print(answer)

