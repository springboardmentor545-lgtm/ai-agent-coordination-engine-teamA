from langchain_core.tools import tool
from pydantic import BaseModel, Field
from app.db import get_supabase
from typing import Optional
from datetime import datetime

class EmergencyAlertInput(BaseModel):
    patient_id: str = Field(description="The unique ID of the patient.")
    alert_reason: str = Field(description="The medical reason for the emergency alert.")

@tool("emergency_alert_tool", args_schema=EmergencyAlertInput)
def emergency_alert_tool(patient_id: str, alert_reason: str) -> str:
    """
    Use this tool when the patient's condition is Critical and life-threatening.
    It dispatches an emergency alert to the hospital dashboard.
    """
    try:
        supabase = get_supabase()
        supabase.table("emergency_alerts").insert({
            "patient_id": patient_id,
            "alert_reason": alert_reason,
            "resolved": False
        }).execute()
        return "SUCCESS: Emergency alert dispatched to the hospital system."
    except Exception as e:
        print(f"Tool error: {e}")
        return f"FAILED to dispatch alert: {e}"

class GuidelineSearchInput(BaseModel):
    symptom_keyword: str = Field(description="The main symptom to search guidelines for.")

@tool("guideline_search_tool", args_schema=GuidelineSearchInput)
def guideline_search_tool(symptom_keyword: str) -> str:
    """
    Use this tool to search standard medical guidelines for a specific symptom.
    Returns the recommended evaluation steps for the symptom.
    """
    guidelines = {
        "chest pain": "Evaluate for ACS (Acute Coronary Syndrome). Check EKG immediately. Administer aspirin if indicated.",
        "headache": "Check for red flags: sudden onset (thunderclap), fever, neck stiffness, neurological deficits.",
        "shortness of breath": "Assess O2 saturation. Consider PE, asthma exacerbation, or heart failure.",
        "abdominal pain": "Rule out appendicitis, ectopic pregnancy, or bowel obstruction. Note location of pain."
    }
    
    keyword = symptom_keyword.lower()
    for key, advice in guidelines.items():
        if key in keyword:
            return advice
            
    return "Standard guideline: Conduct thorough clinical evaluation and consider specialist referral if symptoms persist."

class PatientVitalsInput(BaseModel):
    patient_id: str = Field(description="The unique ID of the patient.")

@tool("patient_vitals_tool", args_schema=PatientVitalsInput)
def patient_vitals_tool(patient_id: str) -> str:
    """
    Use this tool to fetch the patient's most recent vital signs from the database.
    Useful for getting a baseline before analysis.
    """
    # Mocking fetching vitals from an EHR database
    return "Recent Vitals (Mock): HR 82 bpm, BP 120/80 mmHg, SpO2 98%, Temp 98.6 F"

class HospitalLocatorInput(BaseModel):
    department: str = Field(description="The required medical department.")
    urgency: str = Field(description="The urgency level (e.g., Critical, High).")

@tool("hospital_locator_tool", args_schema=HospitalLocatorInput)
def hospital_locator_tool(department: str, urgency: str) -> str:
    """
    Use this tool to find the nearest hospital with an available bed in the specified department.
    """
    if urgency.lower() in ["critical", "high"]:
        return f"Nearest Level 1 Trauma Center with available {department} beds: General Hospital (2.4 miles)."
    return f"Nearest facility for {department}: Community Health Clinic (1.2 miles)."

# List of all tools
ALL_TOOLS = [
    emergency_alert_tool,
    guideline_search_tool,
    patient_vitals_tool,
    hospital_locator_tool
]
