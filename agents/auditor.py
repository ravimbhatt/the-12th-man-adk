from .state import AgentState

def auditor_node(state: AgentState) -> AgentState:
    print("--- [Step 3] Auditor: Calculating ---")
    
    if state.get("final_results") and "error" in state["final_results"]:
        return state

    mappings = state.get("player_mappings", {})
    scores = state.get("match_scores", {})
    
    if not mappings or not scores:
        state["final_results"] = {"error": "Missing data."}
        return state

    leaderboard = {}
    for player, codes in mappings.items():
        total = sum(scores.get(code, 0) for code in codes)
        leaderboard[player] = total

    if not leaderboard:
        state["final_results"] = {"error": "Leaderboard empty."}
        return state

    winner_name = max(leaderboard, key=leaderboard.get)
    winner_score = leaderboard[winner_name]

    settlements = {}
    total_pot = 0.0

    for player, score in leaderboard.items():
        if player != winner_name:
            diff = winner_score - score
            amount = round(diff / 5, 2)
            settlements[player] = amount
            total_pot += amount

    state["final_results"] = {
        "leaderboard": leaderboard,
        "winner": winner_name,
        "winner_score": winner_score,
        "settlements": settlements,
        "total_pot_gbp": round(total_pot, 2)
    }
    return state