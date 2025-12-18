import os
import re

def normalize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

base_folder = os.getcwd()

for folder in os.listdir(base_folder):
    folder_path = os.path.join(base_folder, folder)

    if os.path.isdir(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith(".md") or file.endswith(".txt"):
                file_path = os.path.join(folder_path, file)

                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

                normalized = normalize_text(text)

                output_file = "normalized_" + file
                output_path = os.path.join(folder_path, output_file)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(normalized)

                print(f"Normalized: {file_path}")
