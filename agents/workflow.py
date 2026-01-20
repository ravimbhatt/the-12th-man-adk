from .state import AgentState
from .vision import vision_node
from .scraper import scraper_node
from .auditor import auditor_node
from .analyst import analyst_node
from .forecaster import forecaster_node
from .commentator import commentator_node

def run_workflow(state: AgentState) -> AgentState:
    try:
        # Sequential
        state = vision_node(state)
        if "error" in state.get("final_results", {}): return state

        state = scraper_node(state)
        if "error" in state.get("final_results", {}): return state

        state = auditor_node(state)
        if "error" in state.get("final_results", {}): return state

        # Parallel Intelligence Layer
        # (In a real async system, these would run simultaneously)
        state = analyst_node(state)
        state = forecaster_node(state)
        state = commentator_node(state)
        
        return state

    except Exception as e:
        state["final_results"] = {"error": f"Workflow Error: {str(e)}"}
        return state