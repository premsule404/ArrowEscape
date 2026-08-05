from pydantic import BaseModel
from typing import Dict, Any

class LevelProgressSync(BaseModel):
    level_id: str
    stars: int
    score: int
    
class HintRequest(BaseModel):
    level_id: str
    current_board_state: Dict[str, Any]
