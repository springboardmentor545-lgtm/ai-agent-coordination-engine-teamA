from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agents.foundation_agent import FoundationAgent

router = APIRouter()

agent = FoundationAgent()


class UserRequest(BaseModel):
    user_input: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User prompt for the AI agent",
    )


@router.post("/chat")
def chat(request: UserRequest):
    try:
        response = agent.run(request.user_input)

        return {
            "response": response
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="AI agent failed to process the request.",
        ) from exc