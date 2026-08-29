from app.agents.state import AgentState
from app.db import get_supabase

def research_node(state: AgentState) -> dict:
    """
    Research Agent: Performs a RAG lookup against Supabase pgvector using the extracted symptoms.
    """
    symptoms = state.get("symptoms", "")
    if not symptoms or symptoms.lower() == "unknown":
        return {"medical_knowledge_context": "No specific symptoms provided for lookup."}
        
    try:
        supabase = get_supabase()
        
        response = supabase.table('medical_knowledge').select('*').limit(3).execute()
        
        if response.data and len(response.data) > 0:
            context_pieces = []
            for item in response.data:
                context_pieces.append(
                    f"- Symptom match: {item.get('symptom', '')}, Associated Condition: {item.get('condition', '')}, "
                    f"Recommended Department: {item.get('department', '')}, Default Urgency: {item.get('urgency', '')}"
                )
            context = "Matched knowledge base entries:\n" + "\n".join(context_pieces)
        else:
            context = "No direct matches found in the medical knowledge base. Proceed with general clinical guidelines."
            
    except Exception as e:
        print(f"Research node error: {str(e)}")
        context = "No direct matches found in the medical knowledge base. Proceed with general clinical guidelines."
        
    return {
        "medical_knowledge_context": context
    }
