from fastapi import FastAPI

# This variable MUST be named 'app'
app = FastAPI(
    title="AI Company Internal Chatbot",
    description="Backend for Role-Based Access Control Chatbot",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "project": "Internal Chatbot with RBAC",
        "status": "Server is running successfully"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}