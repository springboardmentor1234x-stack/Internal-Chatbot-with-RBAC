import os
import re
import csv

def clean_text(line):
    line = line.lower()
    line = re.sub(r"[#*`~|├──└──]", "", line)
    line = re.sub(r"[ \t]+", " ", line).rstrip()
    line = re.sub(r"-{2,}", " ", line)
    line = re.sub(r"(?<=[a-zA-Z])-(?=[a-zA-Z])", " ", line)
    line = re.sub(r"\s*-\s*", "", line)
    line = re.sub(r"\n+", "\n", line)
    return line

def normalize_md_file(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    cleaned_lines = [clean_text(line) for line in lines]

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(cleaned_lines))

def normalize_csv_file(input_path, output_path):
    cleaned_lines = []

    with open(input_path, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            line = " ".join(row)       
            line = clean_text(line)   
            cleaned_lines.append(line)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("\n".join(cleaned_lines))

def main(INPUT_ROOT, OUTPUT_ROOT):
    for root, _, files in os.walk(INPUT_ROOT):
        for file in files:
            input_file_path = os.path.join(root, file)

            relative_path = os.path.relpath(root, INPUT_ROOT)
            output_folder_path = os.path.join(OUTPUT_ROOT, relative_path)
            os.makedirs(output_folder_path, exist_ok=True)

            file_name, ext = os.path.splitext(file)
            output_file_path = os.path.join(output_folder_path, file_name + "_cleaned.txt")

            try:
                if ext.lower() == ".md":
                    normalize_md_file(input_file_path, output_file_path)
                    print(f"MD normalized: {output_file_path}")

                elif ext.lower() == ".csv":
                    normalize_csv_file(input_file_path, output_file_path)
                    print(f"CSV normalized: {output_file_path}")

            except Exception as e:
                print(f"Error processing {input_file_path}: {e}")

if __name__ == "__main__":

    # ROOT INPUT & OUTPUT DIRECTORIES
    INPUT_ROOT = "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/Fintech-data"
    OUTPUT_ROOT = "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/Fintech-data-normalized"

    os.makedirs(OUTPUT_ROOT, exist_ok=True)

    main(INPUT_ROOT, OUTPUT_ROOT)
    print("\nALL FILES NORMALIZED SUCCESSFULLY.")
