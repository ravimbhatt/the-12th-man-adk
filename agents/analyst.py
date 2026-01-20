import os
from google import genai
from .state import AgentState

def analyst_node(state: AgentState) -> AgentState:
    print("--- [Agent 4] Analyst: Generating Insights ---")
    
    res = state.get("final_results", {})
    mappings = state.get("player_mappings", {})
    scores = state.get("match_scores", {})
    
    if not res or "error" in res: return state

    winner = res["winner"]
    winner_codes = mappings.get(winner, [])
    
    # Find MVP
    best_code = None
    highest_runs = -1
    for code in winner_codes:
        runs = scores.get(code, 0)
        if runs > highest_runs:
            highest_runs = runs
            best_code = code
            
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    prompt = f"""
    You are a Cricket Data Analyst.
    Winner: {winner} (Codes: {winner_codes}).
    Best Performer: {best_code} ({highest_runs} runs).
    Write a ONE sentence summary of why they won.
    """
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        state["final_results"]["analysis"] = response.text.strip()
    except Exception as e:
        state["final_results"]["analysis"] = f"Led by {best_code} ({highest_runs} runs)."

    return state