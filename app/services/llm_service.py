from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os

# Load environment variables from .env
load_dotenv()

def get_llm():
    """
    Returns a configured Groq LLM instance.
    """
    return ChatGroq(
        model=os.getenv("MODEL_NAME"),
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2,
    )