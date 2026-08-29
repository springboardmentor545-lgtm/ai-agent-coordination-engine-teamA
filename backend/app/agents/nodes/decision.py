from langchain_groq import ChatGroq
from app.agents.state import AgentState
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from pydantic import BaseModel, Field

class DecisionSchema(BaseModel):
    urgency_level: str = Field(description="The assigned urgency level. Must be one of: 'Low', 'Medium', 'High', 'Critical'.")
    recommended_department: str = Field(description="The recommended medical department for the patient (e.g., 'Cardiology', 'General Practice', 'Emergency').")

def decision_node(state: AgentState) -> dict:
    """
    Decision/Triage Agent: Assigns urgency level and recommends department.
    Uses ChatGroq to make a structured decision based on the clinical reasoning.
    """
    reasoning = state.get("analysis_reasoning", "")
    
    try:
        # Initialize LLM
        from langchain_groq import ChatGroq
        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="qwen/qwen3.6-27b", temperature=0.1)
        
        # Define structured output
        structured_llm = llm.with_structured_output(DecisionSchema)
        
        # Define Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the final triage decision maker. Based on the provided clinical reasoning, assign an urgency level ('Low', 'Medium', 'High', 'Critical') and recommend the most appropriate hospital department."),
            ("human", "Clinical Reasoning:\\n{reasoning}")
        ])
        
        # Create chain
        chain = prompt | structured_llm
        
        # Invoke
        result = chain.invoke({"reasoning": reasoning})
        urgency = result.urgency_level
        department = result.recommended_department
        
    except Exception as e:
        print(f"Decision node error: {str(e)}")
        raise RuntimeError(f"Failed to generate triage decision: {str(e)}")
            
    return {
        "urgency_level": urgency,
        "recommended_department": department
    }
