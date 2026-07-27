import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

# Load API key from .env file
load_dotenv()

# Initialize Gemini model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.7
)

def ask_agent(question):
    """Send a question to the agent and get response"""
    response = llm.invoke(question)
    return response.content

# Interactive chat
if __name__ == "__main__":
    print("🤖 Basic AI Agent Started! (Powered by Google Gemini)")
    print("=" * 50)
    print("Type your questions. Type 'exit' to quit.\n")
    
    while True:
        question = input("👤 You: ")
        
        if question.lower() in ["exit", "quit", "bye"]:
            print("🤖 Agent: Goodbye! 👋")
            break
        
        if not question.strip():
            continue
        
        try:
            answer = ask_agent(question)
            print(f"🤖 Agent: {answer}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")