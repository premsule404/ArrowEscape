from pydantic import BaseModel
from typing import Optional

class PlayerStatsSchema(BaseModel):
    user_id: int
    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    replay_count: int = 0
    undo_count: int = 0
    hints_used: int = 0
    avg_completion_time: float = 0.0
    avg_moves: float = 0.0
    fastest_level: Optional[int] = None
    longest_level: Optional[int] = None
    total_arrows_released: int = 0
    total_mistakes: int = 0
    accuracy_pct: float = 100.0

class PlayerStatsUpdateSchema(BaseModel):
    games_played: Optional[int] = None
    games_won: Optional[int] = None
    games_lost: Optional[int] = None
    replay_count: Optional[int] = None
    undo_count: Optional[int] = None
    hints_used: Optional[int] = None
    avg_completion_time: Optional[float] = None
    avg_moves: Optional[float] = None
    fastest_level: Optional[int] = None
    longest_level: Optional[int] = None
    total_arrows_released: Optional[int] = None
    total_mistakes: Optional[int] = None
    accuracy_pct: Optional[float] = None
