from fastapi import FastAPI, HTTPException
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import uvicorn
import re
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_db = Chroma(persist_directory="chroma_db/", embedding_function=embeddings)

ROLE_LINKS = {
    "admin": "https://drive.google.com/drive/folders/1fV7cqvhmVDc6fs5dtFqdWekjKj7EKFnC?ths=true",
    "finance": "https://drive.google.com/drive/folders/1bZw5dZwj9PhzNvR4l9v52QB8n23tjQLQ?ths=true",
    "marketing": "https://drive.google.com/drive/folders/1PGsyJX1RO50t_NlMzNp9MCPS84liC6lv?ths=true",
    "engineering": "https://drive.google.com/drive/folders/1ujLZL8nUlR42qBK9heDQtbq5Ujveh0Y0?ths=true",
    "hr": "https://drive.google.com/drive/folders/1z58iHzKL9-WQxafZqpnR-kOougc_A7Bk?ths=true",
    "intern": "https://drive.google.com/drive/folders/1095TQbx8KvkTa-6XPmj3RvaW45PG6P6Y?ths=true"
}

FILE_VAULT = {
    "finance": ["financial_summary.md", "quarterly_financial_report.md", "budget_2024.csv"],
    "marketing": ["marketing_report_2024.md", "campaign_data.csv", "social_media_stats.csv", "competitor_analysis.md"],
    "hr": ["employee_handbook.md", "payroll_template.csv"],
    "engineering": ["engineering_master_doc.md", "system_architecture.csv"],
    "intern": ["employee_handbook.md"],
    "admin": [] 
}

def clean_output_text(text):
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[|\\*_#\-]', '', text)
    return text.strip()

@app.get("/ask")
async def get_data(role: str, dept: str, query: str):
    role_lower = role.lower()
    dept_lower = dept.lower()
    query_lower = query.lower()
    
    irrelevant_keywords = ["cm", "minister", "prime minister", "cricket", "world cup", "sports", "bollywood", "politics"]
    if any(word in query_lower for word in irrelevant_keywords):
        return {"answer": "## 🚫 Out of Scope\nI am an internal corporate assistant. I am strictly restricted to company documentation and cannot answer general knowledge or political questions."}

    is_privileged = role_lower in ["admin", "ceo"]
    
    
    if not is_privileged and role_lower != dept_lower:
        raise HTTPException(
            status_code=403, 
            detail=f"Access Denied: Your role '{role_lower}' cannot access '{dept_lower}' records."
        )

    if is_privileged:
        search_filter = None
    else:
        allowed_files = FILE_VAULT.get(dept_lower, ["employee_handbook.md"])
        search_filter = {"source": {"$in": allowed_files}}

    results_with_scores = vector_db.similarity_search_with_relevance_scores(
        query, k=3, filter=search_filter
    )
    
    valid_results = [doc for doc, score in results_with_scores if score > 0.22]

    if not valid_results:
        return {"answer": "No relevant authorized information was found for your query in the company dataset."}

    combined_content = " ".join([clean_output_text(d.page_content) for d in valid_results])
    sources = list(set([d.metadata.get("source", "") for d in valid_results]))
    
    detailed_summary = f"## 📖 Analysis Report\n\n{combined_content}\n\n"
    detailed_summary += "### 🔗 Reference Sources & Documentation\n"
    
    if is_privileged:
        folder_url = ROLE_LINKS.get("admin")
    else:
        folder_url = ROLE_LINKS.get(role_lower, ROLE_LINKS["intern"])

    for src in sources:
        allowed_for_role = FILE_VAULT.get(role_lower, ["employee_handbook.md"])
        
        if is_privileged or src in allowed_for_role:
            detailed_summary += f"- **File:** `{src}` | [View in Google Drive]({folder_url})\n"
        else:
            detailed_summary += f"- **File:** `{src}` | (Access Restricted)\n"
    
    return {"answer": detailed_summary}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)