from .state import AgentState

def forecaster_node(state: AgentState) -> AgentState:
    print("--- [Agent 5] Forecaster: Identifying Trends ---")
    
    scores = state.get("match_scores", {})
    if not scores: return state
        
    mvp_code = max(scores, key=scores.get)
    mvp_score = scores[mvp_code]
    
    state["final_results"]["forecast"] = {
        "hot_pick": mvp_code,
        "reason": f"Scored {mvp_score} runs (Match High)",
        "recommendation": "Buy for next round."
    }
    return state