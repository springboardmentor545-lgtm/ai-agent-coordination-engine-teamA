from app.prompts.foundation_prompt import foundation_prompt
from app.services.llm_service import llm


class FoundationAgent:

    def run(self, user_input: str):

        chain = foundation_prompt | llm

        response = chain.invoke(
            {
                "user_input": user_input
            }
        )

        return response.content