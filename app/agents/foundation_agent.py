from fastapi import HTTPException

from app.prompts.foundation_prompt import foundation_prompt
from app.services.llm_service import get_llm


class FoundationAgent:
    """
    Foundation AI Agent responsible for processing user prompts
    and generating responses using the configured LLM.
    """

    def __init__(self):
        self.llm = get_llm()

    def run(self, user_input: str) -> str:
        """
        Executes the prompt chain and returns the model response.
        """
        try:
            chain = foundation_prompt | self.llm

            response = chain.invoke(
                {
                    "user_input": user_input
                }
            )

            return response.content

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate response: {str(e)}"
            )