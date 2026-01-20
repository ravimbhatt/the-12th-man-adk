from typing import TypedDict, List, Dict, Optional, Any

class AgentState(TypedDict):
    image_bytes: List[bytes]
    match_url: str                 # URL 1: For Scores
    commentary_url: str            # URL 2: For Context/Roasting
    player_mappings: Dict[str, List[str]]
    match_scores: Dict[str, int]
    match_commentary: List[str]
    final_results: Optional[Dict[str, Any]]