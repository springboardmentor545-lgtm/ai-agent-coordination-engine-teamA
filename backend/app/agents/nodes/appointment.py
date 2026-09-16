from app.agents.state import AgentState
<<<<<<< HEAD
from app.db import get_supabase
=======
>>>>>>> team/main
import uuid
from datetime import datetime, timedelta

def appointment_node(state: AgentState) -> dict:
    """
    Appointment Agent: Checks availability and books slot.
<<<<<<< HEAD
    Calculates queue-wise dynamic scheduling.
    """
    department = state.get("recommended_department", "General Practice")
    
    # Base time is tomorrow at 9:00 AM
    tomorrow = datetime.now() + timedelta(days=1)
    base_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    
    # Calculate queue length to offset time (queue-wise booking)
    offset_minutes = 0
    try:
        supabase = get_supabase()
        # Find how many pending triages exist to simulate a queue
        res = supabase.table("triages").select("id").eq("status", "pending").execute()
        if res.data:
            queue_length = len(res.data)
            offset_minutes = queue_length * 30 # 30 mins per patient
    except Exception as e:
        print(f"Failed to get queue length: {e}")
        pass
        
    appointment_time = base_time + timedelta(minutes=offset_minutes)
=======
    (Currently uses a dynamic mock implementation)
    """
    department = state.get("recommended_department", "General Practice")
    
    # Generate a realistic mock appointment time (e.g., tomorrow at 10 AM)
    tomorrow = datetime.now() + timedelta(days=1)
    appointment_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
>>>>>>> team/main
    
    # Generate mock ID
    apt_id = f"apt-{uuid.uuid4().hex[:8]}"
    
<<<<<<< HEAD
    # Format nicely e.g., "9:30 AM on 04 September 2026"
    formatted_time = appointment_time.strftime('%I:%M %p').lstrip('0') + " on " + appointment_time.strftime('%d %B %Y')
    
    return {
        "appointment_status": f"Booked for {formatted_time} in {department}",
=======
    return {
        "appointment_status": f"Booked for {appointment_time.strftime('%Y-%m-%d %H:%M')} in {department}",
>>>>>>> team/main
        "appointment_id": apt_id
    }
