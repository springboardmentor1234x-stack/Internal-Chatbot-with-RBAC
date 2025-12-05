import re

input_file = "D:/Infosys Springboard Virtual Internship 6.0/Internal-Chatbot-with-RBAC/Fintech-data/engineering/engineering_master_doc.md"
output_file = "engineering_master_doc_cleaned.txt"

with open(input_file, "r", encoding="utf-8") as file:
    lines = file.readlines()

cleaned_lines = []

for line in lines:
    # Convert to lowercase
    line = line.lower()

    # Remove ONLY unwanted symbols
    line = re.sub(r"[#*`~]", "", line)

    # Remove extra spaces
    line = re.sub(r"[ \t]+", " ", line).rstrip()

    cleaned_lines.append(line)

# Save cleaned text
with open(output_file, "w", encoding="utf-8") as file:
    file.write("\n".join(cleaned_lines))
