# import os
# import json


# # ==========================================================
# # 1. Configuration
# # ==========================================================
# SOURCE_DIRECTORY = r"C:\Users\HP\Desktop\InternalComapanyChatbot\InternalChatbot_normalized"

# CHUNKS_OUTPUT_FILE = "student_chunks.json"
# METADATA_OUTPUT_FILE = "student_metadata.json"

# MAX_WORDS_PER_CHUNK = 350
# CHUNK_WORD_OVERLAP = 50


# # ==========================================================
# # 2. Role-Based Access Control Mapping
# # ==========================================================
# ACCESS_CONTROL = {
#     "engineering": [
#         "Engineering Lead", "Backend Developer", "Frontend Developer",
#         "DevOps Engineer", "System Architect", "Security Team", "C-Level Executive"
#     ],
#     "finance": [
#         "Finance Manager", "Accounts Team", "Auditor",
#         "Risk Analyst", "CFO", "C-Level Executive"
#     ],
#     "marketing": [
#         "Marketing Manager", "SEO Team", "Content Strategist",
#         "Growth Lead", "CMO", "C-Level Executive"
#     ],
#     "hr": [
#         "HR Manager", "Talent Acquisition", "Compliance Officer",
#         "Payroll Team", "C-Level Executive"
#     ],
#     "general": [
#         "Employees", "Department Heads", "C-Level Executive"
#     ]
# }


# # ==========================================================
# # 3. Utility Functions
# # ==========================================================
# def recover_source_name(cleaned_filename):
#     """
#     Recover original source file name from cleaned file.
#     """
#     if "_cleaned.txt" in cleaned_filename:
#         original_base = cleaned_filename.replace("_cleaned.txt", "")
#         if "hr" in original_base.lower():
#             return original_base + ".csv"
#         return original_base + ".md"
#     return cleaned_filename


# # ==========================================================
# # 4. Chunk & Metadata Storage
# # ==========================================================
# chunk_storage = []
# metadata_storage = []

# unique_chunk_number = 1


# # ==========================================================
# # 5. Chunk Generation Logic
# # ==========================================================
# for folder_path, _, file_list in os.walk(SOURCE_DIRECTORY):

#     current_department = os.path.basename(folder_path).lower()

#     for filename in file_list:

#         if not filename.endswith("_cleaned.txt"):
#             continue

#         complete_file_path = os.path.join(folder_path, filename)
#         original_filename = recover_source_name(filename)

#         # ✅ FIX: Create a stable document_id for deduplication
#         document_id = os.path.splitext(original_filename)[0].lower()

#         print(f"📘 Reading → {current_department}/{filename}")

#         with open(complete_file_path, "r", encoding="utf-8") as file:
#             full_text = file.read()

#         word_list = full_text.split()
#         total_words = len(word_list)

#         read_pointer = 0
#         section_number = 1

#         while read_pointer < total_words:

#             next_pointer = read_pointer + MAX_WORDS_PER_CHUNK
#             selected_words = word_list[read_pointer:next_pointer]
#             extracted_text = " ".join(selected_words)

#             current_chunk_id = f"{current_department.upper()}_{unique_chunk_number}"

#             # -------------------------------
#             # Store Chunk
#             # -------------------------------
#             chunk_storage.append({
#                 "chunk_id": current_chunk_id,
#                 "chunk_text": extracted_text
#             })

#             # -------------------------------
#             # Store Metadata (FIXED)
#             # -------------------------------
#             metadata_storage.append({
#                 "chunk_id": current_chunk_id,
#                 "document_id": document_id,     # ⭐ KEY FIX
#                 "original_file": original_filename,
#                 "department": current_department.capitalize(),
#                 "section_index": section_number,
#                 "word_count": len(selected_words),
#                 "classification": "Confidential",
#                 "permitted_roles": ACCESS_CONTROL.get(
#                     current_department, ["C-Level Executive"]
#                 )
#             })

#             unique_chunk_number += 1
#             section_number += 1
#             read_pointer = next_pointer - CHUNK_WORD_OVERLAP


# # ==========================================================
# # 6. Save Output Files
# # ==========================================================
# with open(CHUNKS_OUTPUT_FILE, "w", encoding="utf-8") as f:
#     json.dump(chunk_storage, f, indent=4)

# with open(METADATA_OUTPUT_FILE, "w", encoding="utf-8") as f:
#     json.dump(metadata_storage, f, indent=4)


# print("\n STUDENT CHUNKING & METADATA GENERATION COMPLETED")
# print(" Chunks File   →", CHUNKS_OUTPUT_FILE)
# print(" Metadata File →", METADATA_OUTPUT_FILE)
# print(" Total Chunks  →", len(chunk_storage))

import os
import json

# ==========================================================
# 1. Configuration
# ==========================================================
SOURCE_DIRECTORY = r"C:\Users\HP\Desktop\InternalComapanyChatbot\InternalChatbot_normalized"

CHUNKS_OUTPUT_FILE = "student_chunks.json"
METADATA_OUTPUT_FILE = "student_metadata.json"

MAX_WORDS_PER_CHUNK = 350
CHUNK_WORD_OVERLAP = 50

# ==========================================================
# 2. Role-Based Access Control Mapping
# ==========================================================
ACCESS_CONTROL = {
    "engineering": [
        "Engineering Lead", "Backend Developer", "Frontend Developer",
        "DevOps Engineer", "System Architect", "Security Team", "C-Level Executive"
    ],
    "finance": [
        "Finance Manager", "Accounts Team", "Auditor",
        "Risk Analyst", "CFO", "C-Level Executive"
    ],
    "marketing": [
        "Marketing Manager", "SEO Team", "Content Strategist",
        "Growth Lead", "CMO", "C-Level Executive"
    ],
    "hr": [
        "HR Manager", "Talent Acquisition", "Compliance Officer",
        "Payroll Team", "C-Level Executive"
    ],
    "general": [
        "Employees", "Department Heads", "C-Level Executive"
    ]
}

# ==========================================================
# 3. Utility Functions
# ==========================================================
def recover_source_name(cleaned_filename):
    """
    Recover original source file name from cleaned file.
    """
    if "_cleaned.txt" in cleaned_filename:
        original_base = cleaned_filename.replace("_cleaned.txt", "")
        if "hr" in original_base.lower():
            return original_base + ".csv"
        return original_base + ".md"
    return cleaned_filename

# ==========================================================
# 4. Chunk & Metadata Storage
# ==========================================================
chunk_storage = []
metadata_storage = []

unique_chunk_number = 1

# ==========================================================
# 5. Chunk Generation Logic
# ==========================================================
for folder_path, _, file_list in os.walk(SOURCE_DIRECTORY):

    current_department = os.path.basename(folder_path).lower()

    for filename in file_list:

        if not filename.endswith("_cleaned.txt"):
            continue

        complete_file_path = os.path.join(folder_path, filename)
        original_filename = recover_source_name(filename)

        document_id = os.path.splitext(original_filename)[0].lower()

        print(f"📘 Reading → {current_department}/{filename}")

        with open(complete_file_path, "r", encoding="utf-8") as file:
            full_text = file.read()

        word_list = full_text.split()
        total_words = len(word_list)

        read_pointer = 0
        section_number = 1

        while read_pointer < total_words:

            next_pointer = read_pointer + MAX_WORDS_PER_CHUNK
            selected_words = word_list[read_pointer:next_pointer]
            extracted_text = " ".join(selected_words)

            # ✅ New chunk ID format: DEPARTMENT_CHUNK_X
            current_chunk_id = f"{current_department.upper()}_CHUNK_{unique_chunk_number}"

            # -------------------------------
            # Store Chunk
            # -------------------------------
            chunk_storage.append({
                "chunk_id": current_chunk_id,
                "chunk_text": extracted_text
            })

            # -------------------------------
            # Store Metadata
            # -------------------------------
            metadata_storage.append({
                "chunk_id": current_chunk_id,
                "document_id": document_id,
                "original_file": original_filename,
                "department": current_department.capitalize(),
                "section_index": section_number,
                "word_count": len(selected_words),
                "classification": "Confidential",
                "permitted_roles": ACCESS_CONTROL.get(
                    current_department, ["C-Level Executive"]
                )
            })

            unique_chunk_number += 1
            section_number += 1
            read_pointer = next_pointer - CHUNK_WORD_OVERLAP

# ==========================================================
# 6. Save Output Files
# ==========================================================
with open(CHUNKS_OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(chunk_storage, f, indent=4)

with open(METADATA_OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(metadata_storage, f, indent=4)

print("\n STUDENT CHUNKING & METADATA GENERATION COMPLETED")
print(" Chunks File   →", CHUNKS_OUTPUT_FILE)
print(" Metadata File →", METADATA_OUTPUT_FILE)
print(" Total Chunks  →", len(chunk_storage))
