from langchain_core.messages import ToolMessage

from app.prompts.foundation_prompt import foundation_prompt
from app.services.llm_service import llm
from app.tools.calculator import calculator_tool
from app.tools.weather import weather_tool


class FoundationAgent:
    """
    Foundation AI Agent with tool-calling capability.
    """

    def __init__(self):
        self.tools = [calculator_tool, weather_tool]

        self.tool_map = {
            tool.name: tool
            for tool in self.tools
        }

        self.llm = llm.bind_tools(self.tools)

    def run(self, user_input: str) -> str:
        """
        Process user input and execute tools selected by the LLM.
        """

        messages = foundation_prompt.invoke(
            {
                "user_input": user_input
            }
        ).to_messages()

        response = self.llm.invoke(messages)

        # No tool requested
        if not response.tool_calls:
            return response.content

        # Add the assistant's tool-call message
        messages.append(response)

        # Execute each requested tool
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            selected_tool = self.tool_map.get(tool_name)

            if selected_tool is None:
                raise RuntimeError(
                    f"Unknown tool requested: {tool_name}"
                )

            tool_result = selected_tool.invoke(tool_args)

            # Add the tool result with the correct tool_call_id
            messages.append(
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"],
                )
            )

        # Ask the LLM to create the final answer
        final_response = self.llm.invoke(messages)

        return final_response.content