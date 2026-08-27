from app.agents.state import AgentState
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from pydantic import BaseModel, Field

class IntakeSchema(BaseModel):
    symptoms: str = Field(description="The core medical symptoms the patient is experiencing")
    duration: str = Field(description="How long the patient has been experiencing the symptoms")
    severity: str = Field(description="The self-reported severity of the symptoms (e.g., mild, moderate, severe, or unknown)")

def intake_node(state: AgentState) -> dict:
    """
    Intake Agent: Parses raw messages from the user to extract structured symptoms.
    """
    messages = state.get("messages", [])
    latest_message = messages[-1].content if messages else ""
    
    # Initialize LLM
    llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="qwen/qwen3.6-27b")
    
    # Define structured output
    structured_llm = llm.with_structured_output(IntakeSchema)
    
    # Check if there is an image
    image_data = state.get("image_data")
    if image_data:
        image_url = image_data if image_data.startswith("data:image") else f"data:image/jpeg;base64,{image_data}"
        msg_content = [
            {"type": "text", "text": latest_message or "Analyze this medical report/image and extract the patient's symptoms."},
            {"type": "image_url", "image_url": {"url": image_url}}
        ]
    else:
        msg_content = latest_message
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert triage intake nurse. Extract the core symptoms, duration, and severity from the patient's message or uploaded medical report. If a value is not mentioned, infer 'unknown'."),
        ("human", "{message}")
    ])
    
    chain = prompt | structured_llm
    
    try:
        result = chain.invoke({"message": msg_content})
        return {
            "symptoms": result.symptoms,
            "duration": result.duration,
            "severity": result.severity,
        }
    except Exception as e:
        print(f"Intake node error: {str(e)}")
        raise RuntimeError(f"Failed to extract symptoms from the message: {str(e)}")
