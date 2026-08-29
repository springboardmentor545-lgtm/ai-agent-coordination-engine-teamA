from langchain_groq import ChatGroq
from app.agents.state import AgentState
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from langchain_core.output_parsers import StrOutputParser

def report_node(state: AgentState) -> dict:
    """
    Report Agent: Generates structured summary and formats response.
    Uses ChatGroq to draft a professional response.
    """
    urgency = state.get("urgency_level", "Unknown")
    dept = state.get("recommended_department", "Unknown")
    reasoning = state.get("analysis_reasoning", "")
    apt_status = state.get("appointment_status", "")
    
    try:
        # Initialize LLM
        from langchain_groq import ChatGroq
        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="qwen/qwen3.6-27b", temperature=0.3)
        
        # Define Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are the final CareTriage AI reporting agent. Summarize the following triage data into a short, empathetic, professional response for the patient. State their urgency level, the recommended department, the clinical reasoning briefly, and their appointment status."),
            ("human", "Urgency: {urgency}\\nDepartment: {dept}\\nReasoning: {reasoning}\\nAppointment Status: {apt_status}")
        ])
        
        # Create chain
        chain = prompt | llm | StrOutputParser()
        
        # Invoke
        summary = chain.invoke({
            "urgency": urgency,
            "dept": dept,
            "reasoning": reasoning,
            "apt_status": apt_status
        })
        import re
        summary = re.sub(r'<think>.*?</think>', '', summary, flags=re.DOTALL).strip()
        
    except Exception as e:
        print(f"Report node error: {str(e)}")
        raise RuntimeError(f"Failed to generate final report: {str(e)}")
    
    # Return as an AI message to append to the message history
    return {
        "final_summary": summary,
        "messages": [AIMessage(content=summary)]
    }
