import os
import re
import csv

def clean_line(text):
    text = text.lower()
    text = re.sub(r"[#*~|├└─]", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"-{2,}", " ", text)
    text = re.sub(r"(?<=[a-zA-Z])-(?=[a-zA-Z])", " ", text)
    text = re.sub(r"\s*-\s*", "", text)
    return text.strip()


def clean_markdown(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned = [clean_line(line) for line in lines]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned))


def clean_csv(input_path, output_path):
    cleaned_rows = []

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            joined = " ".join(row)
            cleaned_rows.append(clean_line(joined))

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_rows))


def normalize_all(input_root, output_root):

    for root, _, files in os.walk(input_root):

        relative_path = os.path.relpath(root, input_root)
        save_folder = os.path.join(output_root, relative_path)
        os.makedirs(save_folder, exist_ok=True)

        for file in files:
            full_input_path = os.path.join(root, file)
            file_name, ext = os.path.splitext(file)

            output_file = os.path.join(save_folder, file_name + "_cleaned.txt")

            try:
                if ext.lower() == ".md":
                    clean_markdown(full_input_path, output_file)
                    print(" Markdown cleaned:", output_file)

                elif ext.lower() == ".csv":
                    clean_csv(full_input_path, output_file)
                    print(" CSV cleaned:", output_file)

            except Exception as e:
                print(" Failed on:", full_input_path)
                print("Reason:", e)


if __name__ == "__main__":

    INPUT_DIR = r"C:\Users\HP\Desktop\InternalComapanyChatbot\InternalChatbot"
    OUTPUT_DIR = r"C:\Users\HP\Desktop\InternalComapanyChatbot\InternalChatbot_normalized"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    normalize_all(INPUT_DIR, OUTPUT_DIR)

    print("\n ALL YOUR DATASETS SUCCESSFULLY NORMALIZED")
