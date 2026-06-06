import os
import uuid
import random
from pathlib import Path
from fastapi import FastAPI, Cookie, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

SESSIONS = {}
FLAG = os.environ.get("FLAG", "ASRCTF{m3rs3nn3_tw1st3r_s3ct0r_pr3d1ct0r_9000}")
SECTORS = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']

def new_session():
    return {"prng": random.Random(), "streak": 0}

class DefendRequest(BaseModel):
    sector: int  # 0-7

@app.get("/api/session")
def create_session(response: Response):
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = new_session()
    response.set_cookie(key="session_id", value=session_id, httponly=True, samesite="lax")
    return {"status": "success", "message": "Radar system initialized."}

@app.get("/api/status")
def get_status(session_id: Optional[str] = Cookie(None)):
    if not session_id or session_id not in SESSIONS:
        raise HTTPException(status_code=401, detail="No active session.")
    return {"streak": SESSIONS[session_id]["streak"]}

@app.get("/api/observe")
def observe_asteroid(session_id: Optional[str] = Cookie(None)):
    if not session_id or session_id not in SESSIONS:
        raise HTTPException(status_code=401, detail="No active session.")
    sess = SESSIONS[session_id]
    raw = sess["prng"].getrandbits(32)
    sector_idx = raw % 8
    return {"raw": raw, "sector": sector_idx, "sector_name": SECTORS[sector_idx]}

@app.post("/api/defend")
def defend(req: DefendRequest, session_id: Optional[str] = Cookie(None)):
    if not session_id or session_id not in SESSIONS:
        raise HTTPException(status_code=401, detail="No active session.")
    if req.sector < 0 or req.sector > 7:
        raise HTTPException(status_code=400, detail="Sector must be 0-7.")

    sess = SESSIONS[session_id]
    raw = sess["prng"].getrandbits(32)
    actual_sector = raw % 8

    if req.sector == actual_sector:
        sess["streak"] += 1
        if sess["streak"] >= 100:
            sess["streak"] = 0
            return {
                "correct": True,
                "streak": 100,
                "message": "Shields synchronized. Alien fleet destroyed.",
                "flag": FLAG
            }
        return {"correct": True, "streak": sess["streak"], "message": "Shield activated!"}
    else:
        sess["streak"] = 0
        # Reveal sector name on failure (only 3 bits, not useful for MT cracking)
        return {
            "correct": False,
            "streak": 0,
            "actual_sector": actual_sector,
            "actual_sector_name": SECTORS[actual_sector],
            "message": f"Shield missed! Asteroid struck sector {SECTORS[actual_sector]}."
        }

@app.get("/")
def index():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/style.css")
def css():
    return FileResponse(BASE_DIR / "style.css")

@app.get("/main.js")
def js():
    return FileResponse(BASE_DIR / "main.js")
