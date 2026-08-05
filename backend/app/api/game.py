from fastapi import APIRouter
from ..schemas.game import LevelProgressSync

router = APIRouter()

@router.post("/sync")
def sync_progress(progress: LevelProgressSync):
    # Mock sync
    return {"status": "success", "synced_level": progress.level_id}

@router.get("/leaderboard")
def get_leaderboard():
    # Mock leaderboard
    return [
        {"rank": 1, "username": "ArrowMaster", "stars": 300},
        {"rank": 2, "username": "PuzzleKing", "stars": 280},
    ]
