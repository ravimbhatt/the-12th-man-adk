import os
from google.cloud import aiplatform
from .state import AgentState

def commentator_node(state: AgentState) -> AgentState:
    print("--- [Agent 6] Commentator: Roasting via Vertex AI (Gemma) ---")
    
    winner = state.get("final_results", {}).get("winner", "Unknown")
    score = state.get("final_results", {}).get("winner_score", 0)
    # Grab first 3 lines of commentary text
    raw_commentary = "\n".join(state.get("match_commentary", [])[:3])
    
    PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
    ENDPOINT_ID = os.getenv("VERTEX_ENDPOINT_ID")
    REGION = os.getenv("GOOGLE_REGION", "us-central1")
    
    if not ENDPOINT_ID:
        print("⚠️ No Endpoint ID. Gemma is offline.")
        state["final_results"]["sarcastic_summary"] = "Gemma is sleeping."
        return state

    try:
        aiplatform.init(project=PROJECT_ID, location=REGION)
        endpoint = aiplatform.Endpoint(ENDPOINT_ID)
        
        # Gemma Prompt Format
        prompt = f"""<start_of_turn>user
You are a sarcastic commentator.
Winner: {winner} ({score} runs).
Context: "{raw_commentary}"
Write a ONE-sentence roasting summary.<end_of_turn>
<start_of_turn>model
"""
        
        instances = [{
            "prompt": prompt,
            "max_tokens": 100,
            "temperature": 0.8,
            "top_p": 0.9
        }]
        
        response = endpoint.predict(instances=instances)
        text = response.predictions[0].strip()
        
        if "<end_of_turn>" in text:
            text = text.split("<end_of_turn>")[0]
            
        state["final_results"]["sarcastic_summary"] = text
        print(f"🎙️ Gemma says: {text}")

    except Exception as e:
        print(f"❌ Vertex AI Error: {e}")
        state["final_results"]["sarcastic_summary"] = f"{winner} won."

    return state