from langchain_groq import ChatGroq
from app.agents.state import AgentState
from langchain_core.messages import AIMessage
<<<<<<< HEAD
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from langchain_core.output_parsers import StrOutputParser
import re

def report_node(state: AgentState) -> dict:
    """
    Report Agent: Generates a professional, structured clinical triage report.
=======
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from langchain_core.output_parsers import StrOutputParser

def report_node(state: AgentState) -> dict:
    """
    Report Agent: Generates structured summary and formats response.
    Uses ChatGroq to draft a professional response.
>>>>>>> team/main
    """
    urgency = state.get("urgency_level", "Unknown")
    dept = state.get("recommended_department", "Unknown")
    reasoning = state.get("analysis_reasoning", "")
    apt_status = state.get("appointment_status", "")
<<<<<<< HEAD
    symptoms = state.get("symptoms", "Not specified")
    duration = state.get("duration", "Not specified")
    severity = state.get("severity", "Not specified")

    urgency_badge = {"High": "🔴 HIGH PRIORITY", "Medium": "🟡 MEDIUM PRIORITY", "Low": "🟢 LOW PRIORITY"}.get(urgency, "⚪ UNDER REVIEW")

    try:
        llm = ChatGroq(api_key=settings.GROQ_API_KEY, model_name="openai/gpt-oss-120b", temperature=0.2)

        prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are the VitalGate AI Chief Medical Reporting Agent. "
             "Generate a professional, structured clinical triage report using the data provided. "
             "Output the report EXACTLY using this format and NO other text:\n\n"
             "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
             "🏥 VITALGATE AI — OFFICIAL TRIAGE REPORT\n"
             "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
             "**URGENCY STATUS:** {urgency_badge}\n"
             "**Recommended Department:** {dept}\n\n"
             "---\n"
             "**📋 PATIENT PRESENTATION**\n"
             "- **Primary Complaint:** [summarize: {symptoms}]\n"
             "- **Duration:** {duration}\n"
             "- **Reported Severity:** {severity}\n\n"
             "---\n"
             "**🔬 CLINICAL ASSESSMENT**\n"
             "[Write 2-3 clear, non-alarming sentences summarizing the likely condition based on: {reasoning}]\n\n"
             "---\n"
             "**✅ RECOMMENDED NEXT STEPS**\n"
             "1. [Immediate action the patient should take right now]\n"
             "2. [What the patient should monitor or track]\n"
             "3. [Warning signs that require emergency care]\n\n"
             "---\n"
             "**📅 APPOINTMENT INFORMATION**\n"
             "{apt_status}\n\n"
             "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
             "⚕️ This report is AI-generated for informational purposes only. It is NOT a substitute for professional medical advice or diagnosis. Please consult a licensed healthcare provider.\n"
             "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ),
            ("human", "Generate the triage report now.")
        ])

        chain = prompt | llm | StrOutputParser()

        summary = chain.invoke({
            "urgency_badge": urgency_badge,
            "dept": dept,
            "symptoms": symptoms,
            "duration": duration,
            "severity": severity,
            "reasoning": reasoning,
            "apt_status": apt_status
        })
        summary = re.sub(r'<think>.*?</think>', '', summary, flags=re.DOTALL).strip()

    except Exception as e:
        print(f"Report node error: {str(e)}")
        raise RuntimeError(f"Failed to generate final report: {str(e)}")

=======
    
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
>>>>>>> team/main
    return {
        "final_summary": summary,
        "messages": [AIMessage(content=summary)]
    }
