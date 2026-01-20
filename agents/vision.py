import os
import json
from google import genai
from google.genai import types
from .state import AgentState

def get_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment.")
    return genai.Client(api_key=api_key)

def vision_node(state: AgentState) -> AgentState:
    print(f"--- [Step 1] Vision: Processing {len(state['image_bytes'])} images ---")
    
    try:
        client = get_client()
        # Default to the fast, multimodal model
        model_name = os.getenv("MODEL_NAME", "gemini-2.5-flash")

        contents_parts = []
        prompt_text = (
            "Analyze these images of a cricket player list. "
            "Extract a JSON mapping where:\n"
            "- Keys are Player Names (string).\n"
            "- Values are a list of their assigned codes (e.g. ['T1-1', 'T2-5']).\n"
            "Return ONLY raw JSON. No markdown formatting."
        )
        contents_parts.append(prompt_text)

        # Attach images
        for img_bytes in state["image_bytes"]:
            contents_parts.append(
                types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg")
            )

        response = client.models.generate_content(
            model=model_name,
            contents=contents_parts,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        # Clean JSON
        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```json", "").replace("```", "")
            
        mappings = json.loads(raw_text)
        state["player_mappings"] = mappings
        return state

    except Exception as e:
        print(f"Vision Error: {e}")
        state["final_results"] = {"error": f"Vision processing failed: {str(e)}"}
        return state