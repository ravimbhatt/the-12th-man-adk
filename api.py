import asyncio
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from agents.workflow import run_workflow

load_dotenv()

app = FastAPI(title="The 12th Man API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/calculate")
async def calculate_settlements(
    match_url: str = Form(...), 
    commentary_url: str = Form(...),
    files: List[UploadFile] = File(...)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    print(f"📥 Processing: {match_url}")

    image_bytes_list = []
    for file in files:
        content = await file.read()
        image_bytes_list.append(content)

    initial_state = {
        "image_bytes": image_bytes_list,
        "match_url": match_url,
        "commentary_url": commentary_url,
        "player_mappings": {},
        "match_scores": {},
        "match_commentary": [],
        "final_results": {}
    }

    try:
        final_state = await asyncio.to_thread(run_workflow, initial_state)
        res = final_state.get("final_results", {})
        
        if "error" in res:
            raise HTTPException(status_code=500, detail=res["error"])

        return {
            "status": "success",
            "data": {
                "winner": res.get("winner"),
                "winner_score": res.get("winner_score"),
                "total_pot": res.get("total_pot_gbp"),
                "sarcastic_summary": res.get("sarcastic_summary"),
                "analysis": res.get("analysis"),
                "forecast": res.get("forecast"),
                "settlements": res.get("settlements"),
                "player_mappings": final_state.get("player_mappings"),
                "detailed_scores": final_state.get("match_scores")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))