from app.agents.foundation_agent import FoundationAgent

agent = FoundationAgent()

response = agent.run("Explain Artificial Intelligence in simple words.")

print(response)