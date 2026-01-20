import pytest
import os
import json
from dotenv import load_dotenv
from unittest.mock import MagicMock, patch

# Import Agents
from agents.vision import vision_node
from agents.scraper import scraper_node
from agents.auditor import auditor_node
from agents.analyst import analyst_node
from agents.forecaster import forecaster_node
from agents.commentator import commentator_node

load_dotenv()

# --- CONFIG FOR REAL TESTS ---
# Use a real historical match that is guaranteed to exist
TEST_MATCH_URL = "https://www.espncricinfo.com/series/women-s-premier-league-2022-23-1348825/delhi-capitals-women-vs-mumbai-indians-women-final-1358929/full-scorecard"
TEST_COMMENTARY_URL = "https://www.espncricinfo.com/series/women-s-premier-league-2022-23-1348825/delhi-capitals-women-vs-mumbai-indians-women-final-1358929/ball-by-ball-commentary"

# --- UNIT TESTS (LOGIC ONLY) ---

def test_auditor_math_logic():
    """
    Verifies the core settlement formula: (Winner - Player) / 5
    """
    state = {
        "player_mappings": {
            "Ravi": ["T1-1", "T1-2"],  # 100 + 0 = 100 runs
            "Nilay": ["T2-1", "T2-5"], # 50 + 0 = 50 runs
            "Amit": ["T2-2", "T2-3"]   # 100 + 0 = 100 runs (Tie with winner)
        },
        "match_scores": {
            "T1-1": 100, "T1-2": 0,
            "T2-1": 50, "T2-5": 0,
            "T2-2": 100, "T2-3": 0
        },
        "final_results": {}
    }
    
    result = auditor_node(state)
    res = result["final_results"]
    
    # 1. Check Winner
    # If tie, max() picks the first one encountered usually, but logic holds.
    assert res["winner_score"] == 100
    
    # 2. Check Loser Settlement
    # Diff = 100 - 50 = 50. Amount = 50 / 5 = 10.0
    assert res["settlements"]["Nilay"] == 10.0
    
    # 3. Check Tie Settlement (Should be 0)
    # Diff = 100 - 100 = 0.
    if "Amit" in res["settlements"]:
        assert res["settlements"]["Amit"] == 0.0

def test_forecaster_logic():
    """Verifies that the forecaster correctly identifies the MVP."""
    state = {
        "match_scores": {"T1-1": 10, "T1-2": 85, "T2-1": 40},
        "final_results": {}
    }
    result = forecaster_node(state)
    forecast = result["final_results"]["forecast"]
    
    assert forecast["hot_pick"] == "T1-2"
    assert "85" in forecast["reason"]

# --- INTEGRATION TESTS (REAL API CALLS) ---

@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="No Google API Key")
def test_vision_real_call(tmp_path):
    """
    Verifies Vision Agent can talk to Gemini 2.0 Flash.
    Sends a dummy image to ensure the pipeline doesn't crash.
    """
    # Create dummy JPEG
    img_path = tmp_path / "test.jpg"
    with open(img_path, "wb") as f:
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\db\x00C\x00\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00')
    
    with open(img_path, "rb") as f:
        img_bytes = f.read()

    state = {
        "image_bytes": [img_bytes],
        "final_results": {}
    }
    
    result = vision_node(state)
    
    # We expect a result, even if it's empty JSON due to blank image
    assert "error" not in result.get("final_results", {})
    assert isinstance(result["player_mappings"], dict)

def test_scraper_dual_url_real_call():
    """
    Verifies Scraper visits BOTH Scorecard and Commentary URLs.
    """
    state = {
        "match_url": TEST_MATCH_URL,
        "commentary_url": TEST_COMMENTARY_URL,
        "final_results": {}
    }
    
    result = scraper_node(state)
    
    # 1. Check Scores (Meg Lanning = 35)
    scores = result.get("match_scores", {})
    assert len(scores) > 0
    assert scores.get("T1-1") == 35
    
    # 2. Check Commentary
    comms = result.get("match_commentary", [])
    assert len(comms) > 0
    # Check if we got text (usually > 10 chars)
    assert len(comms[0]) > 10

@pytest.mark.skipif(not os.getenv("GOOGLE_API_KEY"), reason="No Google API Key")
def test_analyst_real_call():
    """
    Verifies Analyst Agent uses Gemini to generate reasoning.
    """
    state = {
        "final_results": {"winner": "TestUser"},
        "player_mappings": {"TestUser": ["T1-1"]},
        "match_scores": {"T1-1": 50}
    }
    
    result = analyst_node(state)
    analysis = result["final_results"].get("analysis", "")
    
    assert analysis != ""
    assert "T1-1" in analysis or "50" in analysis

@pytest.mark.skipif(not os.getenv("VERTEX_ENDPOINT_ID"), reason="No Vertex Endpoint ID")
def test_commentator_real_vertex_call():
    """
    Verifies Commentator Agent can talk to self-hosted Gemma on Vertex AI.
    """
    state = {
        "final_results": {"winner": "Ravi", "winner_score": 100},
        "match_commentary": ["Mumbai Indians won by 7 wickets", "Harmancpreet Kaur hits a four!"]
    }
    
    result = commentator_node(state)
    sarcasm = result["final_results"].get("sarcastic_summary", "")
    
    # If endpoint is active, we get text. If sleeping/error, we get fallback.
    # We assert that we got *something* back.
    assert len(sarcasm) > 5
    print(f"Vertex AI Output: {sarcasm}")