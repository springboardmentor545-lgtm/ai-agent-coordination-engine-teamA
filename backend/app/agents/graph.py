from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.nodes.intake import intake_node
from app.agents.nodes.research import research_node
from app.agents.nodes.analysis import analysis_node
from app.agents.nodes.decision import decision_node
from app.agents.nodes.appointment import appointment_node
from app.agents.nodes.report import report_node
from app.agents.nodes.coordinator import coordinator_node

def route_coordinator(state: AgentState):
    route = state.get("route", "normal_track")
    if route == "fast_track":
        return "fast_track"
    return "normal_track"

<<<<<<< HEAD
import time
import logging

logger = logging.getLogger(__name__)

def log_node_execution(name: str, func):
    def wrapper(state: AgentState):
        logger.info(f"[AGENT EXECUTION] Starting {name} Agent...")
        start_t = time.time()
        try:
            result = func(state)
            duration = (time.time() - start_t) * 1000
            logger.info(f"[AGENT COMPLETED] {name} Agent finished successfully in {duration:.2f}ms")
            return result
        except Exception as e:
            logger.error(f"[AGENT FAILED] {name} Agent encountered an error: {str(e)}")
            raise
    return wrapper

=======
>>>>>>> team/main
def create_triage_graph():
    # Initialize Graph
    workflow = StateGraph(AgentState)
    
<<<<<<< HEAD
    # Add Nodes with Logging Wrappers
    workflow.add_node("coordinator", log_node_execution("Coordinator", coordinator_node))
    workflow.add_node("intake", log_node_execution("Intake", intake_node))
    workflow.add_node("research", log_node_execution("Research", research_node))
    workflow.add_node("analysis", log_node_execution("Analysis", analysis_node))
    workflow.add_node("decision", log_node_execution("Decision", decision_node))
    workflow.add_node("appointment", log_node_execution("Appointment", appointment_node))
    workflow.add_node("report", log_node_execution("Report", report_node))
=======
    # Add Nodes
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("intake", intake_node)
    workflow.add_node("research", research_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("decision", decision_node)
    workflow.add_node("appointment", appointment_node)
    workflow.add_node("report", report_node)
>>>>>>> team/main
    
    # Define Edges (The Pipeline)
    workflow.set_entry_point("coordinator")
    
    # Conditional Routing from Coordinator
    workflow.add_conditional_edges(
        "coordinator",
        route_coordinator,
        {
            "fast_track": "decision",
            "normal_track": "intake"
        }
    )
    
    workflow.add_edge("intake", "research")
    workflow.add_edge("research", "analysis")
    workflow.add_edge("analysis", "decision")
    
    # Conditional logic can be added here, but for now we follow the linear path
    workflow.add_edge("decision", "appointment")
    workflow.add_edge("appointment", "report")
    workflow.add_edge("report", END)
    
    # Compile
    return workflow.compile()

triage_app = create_triage_graph()
