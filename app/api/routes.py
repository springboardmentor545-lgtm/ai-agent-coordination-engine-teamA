from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.foundation_agent import FoundationAgent

router = APIRouter()

agent = FoundationAgent()


class ChatRequest(BaseModel):
    user_input: str


class ChatResponse(BaseModel):
    response: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = agent.run(request.user_input)
    return ChatResponse(response=response)