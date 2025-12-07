import re
import string
from nltk.stem import WordNetLemmatizer

def normalize_text(text, use_lemmatization=False):
  
    text = text.lower()

    allowed = string.ascii_lowercase + string.digits + " .,;:%'-\n"
    text = ''.join(char for char in text if char in allowed)

    text = re.sub(r'\s+', ' ', text)

    text = text.replace(". ", ".\n")

    text = re.sub(r'\n+', '\n', text)

    if use_lemmatization:
        lemmatizer = WordNetLemmatizer()
        words = text.split()
        words = [lemmatizer.lemmatize(w) for w in words]
        text = ' '.join(words)

    return text


input_file = "marketing_report_raw.txt"
output_file = "marketing_report_cleaned.txt"

with open(input_file, "r", encoding="utf-8") as f:
    raw_text = f.read()

cleaned_text = normalize_text(raw_text, use_lemmatization=False)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(cleaned_text)

print("Text normalization complete!")
print(f"Cleaned file saved as: {output_file}")

