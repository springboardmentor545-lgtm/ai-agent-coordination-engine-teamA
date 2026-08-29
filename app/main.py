from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="AI Agent Coordination Engine",
    version="1.0"
)

app.include_router(router)

@app.get("/")
def home():
    return {
        "message": "Welcome to AI Agent Coordination Engine",
        "docs": "http://127.0.0.1:8000/docs"
    }