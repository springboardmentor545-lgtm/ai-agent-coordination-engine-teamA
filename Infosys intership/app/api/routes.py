from fastapi import APIRouter
from pydantic import BaseModel

from app.agents.foundation_agent import FoundationAgent

router = APIRouter()

agent = FoundationAgent()

class UserRequest(BaseModel):
    user_input: str

@router.post("/chat")
def chat(request: UserRequest):
    response = agent.run(request.user_input)
    return {"response": response}