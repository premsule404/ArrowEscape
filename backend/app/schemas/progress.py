from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class LevelSyncItem(BaseModel):
    level_id: int
    stars: int
    moves: int
    time: float
    base_coins: int = 100
    completed: bool = True

class CloudSyncRequest(BaseModel):
    levels: List[LevelSyncItem] = []
    total_coins: Optional[int] = None
    total_stars: Optional[int] = None
    current_level: Optional[int] = None
    theme: Optional[str] = None
    color_tutorial_dismissed: Optional[bool] = None

class CloudSyncResponse(BaseModel):
    success: bool = True
    total_coins: int
    total_stars: int
    completed_count: int
    highest_unlocked_level: int
    levels: List[Dict[str, Any]]
