from langchain_core.prompts import ChatPromptTemplate

foundation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a helpful AI assistant. "
                "Provide clear, accurate, and concise responses."
            ),
        ),
        (
            "human",
            "{user_input}",
        ),
    ]
)