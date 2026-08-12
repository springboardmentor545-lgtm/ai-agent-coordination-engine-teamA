from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage

from app.main import app
from app.api.routes import agent


client = TestClient(app)


# -------------------------
# FastAPI tests
# -------------------------

def test_chat_success():
    original_run = agent.run
    agent.run = Mock(return_value="Hello from the AI agent.")

    try:
        response = client.post(
            "/chat",
            json={"user_input": "Hello"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "response": "Hello from the AI agent."
        }

    finally:
        agent.run = original_run


def test_chat_empty_input():
    response = client.post(
        "/chat",
        json={"user_input": ""},
    )

    assert response.status_code == 422


def test_chat_input_too_long():
    response = client.post(
        "/chat",
        json={"user_input": "a" * 2001},
    )

    assert response.status_code == 422


def test_chat_agent_error():
    original_run = agent.run
    agent.run = Mock(
        side_effect=ValueError("Invalid request")
    )

    try:
        response = client.post(
            "/chat",
            json={"user_input": "test"},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid request"

    finally:
        agent.run = original_run


# -------------------------
# FoundationAgent tests
# -------------------------

def test_agent_normal_response():
    """Agent should return the LLM response when no tool is requested."""

    from app.agents.foundation_agent import FoundationAgent

    foundation_agent = FoundationAgent()

    foundation_agent.llm = Mock(
        invoke=Mock(
            return_value=AIMessage(
                content="An AI agent is an autonomous AI system.",
                tool_calls=[],
            )
        )
    )

    result = foundation_agent.run("What is an AI agent?")

    assert result == "An AI agent is an autonomous AI system."
    foundation_agent.llm.invoke.assert_called_once()


def test_agent_calculator_tool():
    """Agent should execute the calculator when the LLM requests it."""

    from app.agents.foundation_agent import FoundationAgent

    foundation_agent = FoundationAgent()

    first_response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "calculator_tool",
                "args": {"expression": "25 * 40"},
                "id": "calculator-call-1",
                "type": "tool_call",
            }
        ],
    )

    final_response = AIMessage(
        content="The result is 1000.",
        tool_calls=[],
    )

    foundation_agent.llm = Mock(
        invoke=Mock(
            side_effect=[
                first_response,
                final_response,
            ]
        )
    )

    result = foundation_agent.run(
        "What is 25 multiplied by 40?"
    )

    assert result == "The result is 1000."
    assert foundation_agent.llm.invoke.call_count == 2


def test_agent_weather_tool():
    """Agent should execute the weather tool when requested."""

    from app.agents.foundation_agent import FoundationAgent

    foundation_agent = FoundationAgent()

    first_response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "weather_tool",
                "args": {"city": "Hyderabad"},
                "id": "weather-call-1",
                "type": "tool_call",
            }
        ],
    )

    final_response = AIMessage(
        content="Hyderabad is currently 24°C.",
        tool_calls=[],
    )

    foundation_agent.llm = Mock(
        invoke=Mock(
            side_effect=[
                first_response,
                final_response,
            ]
        )
    )

    with patch(
        "langchain_core.tools.BaseTool.invoke",
        return_value=(
            "Weather in Hyderabad, India: "
            "24°C, humidity 80%, wind speed 8 km/h."
        ),
    ) as mock_invoke:

        result = foundation_agent.run(
            "What is the current weather in Hyderabad?"
        )

        assert result == "Hyderabad is currently 24°C."

        mock_invoke.assert_called_once_with(
            {"city": "Hyderabad"}
        )

        assert foundation_agent.llm.invoke.call_count == 2