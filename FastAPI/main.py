from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from FastAPI.routes.chat import router as chat_router

app = FastAPI(
    title="Internal Role-Based Access Control Chatbot",
    description="FastAPI backend for a company RBAC chatbot",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register chatbot routes
app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": "RBAC Chatbot API is running"}
