import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as chat_router

app = FastAPI(title="FinSolve Backend API")

# Fixes the "Cannot connect" error by allowing cross-port communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connects your endpoints defined in routes.py
app.include_router(chat_router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "Online", "message": "FastAPI is running on port 8000"}

if __name__ == "__main__":
    # Standard FastAPI port is 8000
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)