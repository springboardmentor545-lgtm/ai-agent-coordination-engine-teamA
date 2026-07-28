from app.agents.foundation_agent import FoundationAgent


def test_foundation_agent():
    agent = FoundationAgent()

    response = agent.run("What is an AI agent?")

    assert isinstance(response, str)
    assert len(response.strip()) > 0