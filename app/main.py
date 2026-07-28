from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="AI Agent Coordination Engine",
    description="Foundation AI Agent using Groq and LangChain",
    version="1.0.0",
)

app.include_router(router)