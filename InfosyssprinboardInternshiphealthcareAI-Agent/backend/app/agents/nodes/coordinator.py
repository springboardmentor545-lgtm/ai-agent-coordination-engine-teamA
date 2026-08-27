from app.agents.state import AgentState

def coordinator_node(state: AgentState) -> dict:
    """
    Coordinator Agent: Decides if the patient needs to be fast-tracked to decision or go through full intake/research.
    """
    messages = state.get("messages", [])
    if not messages:
        return {"route": "normal_track"}
    
    latest_msg = messages[-1].content.lower()
    
    # Emergency fast tracking
    emergency_keywords = ["severe", "bleeding", "heart attack", "stroke", "unconscious", "chest pain", "emergency", "can't breathe"]
    
    route = "normal_track"
    if any(keyword in latest_msg for keyword in emergency_keywords):
        route = "fast_track"
        
    return {
        "route": route,
        "symptoms": latest_msg
    }
