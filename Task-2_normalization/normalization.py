import os
import re
import csv
from datetime import datetime


# ---------------- CONFIGURATION ----------------
SUPPORTED_EXTENSIONS = [".md", ".txt", ".csv"]
LOG_FILE = "normalization_log.txt"


# ---------------- LOGGING ----------------
def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {message}\n")


# ---------------- TEXT CLEANING ----------------
def remove_markdown_symbols(text):
    return re.sub(r"[#*>`_|]", " ", text)


def clean_special_characters(text):
    return re.sub(r"[^a-zA-Z0-9\s]", " ", text)


def normalize_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()


def full_text_normalization(text):
    text = text.lower()
    text = remove_markdown_symbols(text)
    text = clean_special_characters(text)
    text = normalize_whitespace(text)
    return text


# ---------------- FILE HANDLERS ----------------
def process_text_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    normalized_content = full_text_normalization(content)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(normalized_content)

    write_log(f"Text normalized: {input_path}")


def process_csv_file(input_path, output_path):
    normalized_rows = []

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            normalized_rows.append(
                full_text_normalization(" ".join(row))
            )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(normalized_rows))

    write_log(f"CSV normalized: {input_path}")


# ---------------- DIRECTORY WALKER ----------------
def normalize_directory(input_root, output_root):
    for root, _, files in os.walk(input_root):
        # Skip output folder to avoid re-processing
        if output_root in root:
            continue

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            input_file = os.path.join(root, file)

            relative_path = os.path.relpath(root, input_root)
            output_dir = os.path.join(output_root, relative_path)
            os.makedirs(output_dir, exist_ok=True)

            output_file = os.path.join(
                output_dir,
                os.path.splitext(file)[0] + "_normalized.txt"
            )

            try:
                if ext == ".csv":
                    process_csv_file(input_file, output_file)
                else:
                    process_text_file(input_file, output_file)

                print(f"Normalized: {input_file}")

            except Exception as e:
                write_log(f"ERROR processing {input_file}: {e}")


# ---------------- MAIN ----------------
def main():
    input_folder = "."   # CURRENT DIRECTORY
    output_folder = "Fintech-data-normalized"

    os.makedirs(output_folder, exist_ok=True)
    write_log("Normalization process started")

    normalize_directory(input_folder, output_folder)

    write_log("Normalization process completed")
    print("\nALL FILES NORMALIZED SUCCESSFULLY.")


if __name__ == "__main__":
    main()
