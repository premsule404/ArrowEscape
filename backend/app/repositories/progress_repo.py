from sqlalchemy.orm import Session
from typing import Optional, List
from ..models.user import UserProgressSummary
from ..models.game import LevelProgress

class ProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self, user_id: int) -> Optional[UserProgressSummary]:
        return self.db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user_id).first()

    def get_or_create_summary(self, user_id: int) -> UserProgressSummary:
        summary = self.get_summary(user_id)
        if not summary:
            summary = UserProgressSummary(user_id=user_id, current_level=1, highest_unlocked_level=1)
            self.db.add(summary)
            self.db.commit()
            self.db.refresh(summary)
        return summary

    def get_level_progress(self, user_id: int, level_num: int) -> Optional[LevelProgress]:
        return self.db.query(LevelProgress).filter(
            LevelProgress.user_id == user_id,
            LevelProgress.level_num == level_num
        ).first()

    def get_all_level_progress(self, user_id: int) -> List[LevelProgress]:
        return self.db.query(LevelProgress).filter(LevelProgress.user_id == user_id).all()

    def update_level_progress(self, user_id: int, level_num: int, stars: int, moves: int, time_taken: float, coins_claimed: int, completed: bool = True) -> LevelProgress:
        lvl = self.get_level_progress(user_id, level_num)
        if not lvl:
            lvl = LevelProgress(user_id=user_id, level_num=level_num, unlocked=True, stars=0, best_moves=0, best_time=0.0, coins_claimed=0)
            self.db.add(lvl)
            
        old_moves = lvl.best_moves or 0
        old_time = lvl.best_time or 0.0
        
        lvl.stars = max(lvl.stars or 0, stars)
        lvl.coins_claimed = max(lvl.coins_claimed or 0, coins_claimed)
        lvl.best_moves = moves if (old_moves == 0 or moves < old_moves) else old_moves
        lvl.best_time = time_taken if (old_time == 0.0 or time_taken < old_time) else old_time
        lvl.completed = lvl.completed or completed
        lvl.attempts = (lvl.attempts or 0) + 1
        
        self.db.commit()
        self.db.refresh(lvl)
        return lvl
