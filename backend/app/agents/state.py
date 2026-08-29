from typing import TypedDict, Annotated, List, Optional
import operator
from pydantic import BaseModel, Field

class AgentState(TypedDict):
    # Chat history / Input
    messages: Annotated[list, operator.add]
    patient_id: str
    image_data: Optional[str]
    
    # Extracted fields from Intake
    symptoms: str
    duration: str
    severity: str
    
    # Retrieved knowledge
    medical_knowledge_context: str
    
    # Analysis outputs
    analysis_reasoning: str
    
    # Decision / Triage outputs
    urgency_level: str
    recommended_department: str
    suspected_condition: str
    
    # Appointment output
    appointment_status: str
    appointment_id: Optional[str]
    
    # Final report
    report_id: Optional[str]
    final_summary: str
    
    # Next node to route to
    next_node: str
