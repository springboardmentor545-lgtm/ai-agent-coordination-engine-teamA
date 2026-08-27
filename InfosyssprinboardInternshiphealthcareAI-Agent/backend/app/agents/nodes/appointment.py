from app.agents.state import AgentState
import uuid
from datetime import datetime, timedelta

def appointment_node(state: AgentState) -> dict:
    """
    Appointment Agent: Checks availability and books slot.
    (Currently uses a dynamic mock implementation)
    """
    department = state.get("recommended_department", "General Practice")
    
    # Generate a realistic mock appointment time (e.g., tomorrow at 10 AM)
    tomorrow = datetime.now() + timedelta(days=1)
    appointment_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    # Generate mock ID
    apt_id = f"apt-{uuid.uuid4().hex[:8]}"
    
    return {
        "appointment_status": f"Booked for {appointment_time.strftime('%Y-%m-%d %H:%M')} in {department}",
        "appointment_id": apt_id
    }
