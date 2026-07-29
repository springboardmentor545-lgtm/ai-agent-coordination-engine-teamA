import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# Read API Key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ Groq API Key not found!")
    exit()

# Initialize Groq Model
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=api_key,
    temperature=0.3
)

# Prompt
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an Enterprise AI Agent. Answer professionally and clearly."
    ),
    ("human", "{query}")
])

# Chat Loop
print("=" * 50)
print("🤖 Enterprise AI Agent")
print("Type 'exit' to quit")
print("=" * 50)

while True:
    query = input("\nYou: ")

    if query.lower() == "exit":
        print("Goodbye 👋")
        break

    chain = prompt | llm
    response = chain.invoke({"query": query})

    print("\nAgent:")
    print(response.content)