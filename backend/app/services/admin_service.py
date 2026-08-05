from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..repositories.player_repo import PlayerRepository
from ..repositories.progress_repo import ProgressRepository
from ..services.store_service import StoreService
from ..models.user import User

class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.player_repo = PlayerRepository(db)
        self.progress_repo = ProgressRepository(db)
        self.store_service = StoreService(db)

    def list_all_users(self, limit: int = 50) -> List[Dict[str, Any]]:
        users = self.db.query(User).order_by(User.id.asc()).limit(limit).all()
        res = []
        for u in users:
            summary = self.progress_repo.get_summary(u.id)
            res.append({
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "is_guest": u.is_guest,
                "created_at": u.created_at,
                "current_level": summary.current_level if summary else 1,
                "highest_unlocked_level": summary.highest_unlocked_level if summary else 1,
                "total_coins": summary.total_coins if summary else 0,
                "total_stars": summary.total_stars if summary else 0
            })
        return res

    def grant_user_coins(self, target_user_id: int, amount: int) -> int:
        return self.store_service.grant_coins(target_user_id, amount, source="admin_adjustment")

    def unlock_user_levels(self, target_user_id: int, level_to_unlock: int) -> int:
        summary = self.progress_repo.get_or_create_summary(target_user_id)
        summary.highest_unlocked_level = min(50, max(summary.highest_unlocked_level or 1, level_to_unlock))
        self.db.commit()
        return summary.highest_unlocked_level

    def reset_user_progress(self, target_user_id: int) -> bool:
        summary = self.progress_repo.get_or_create_summary(target_user_id)
        summary.current_level = 1
        summary.highest_unlocked_level = 1
        summary.completed_levels = 0
        summary.total_stars = 0
        summary.total_coins = 0
        self.db.commit()
        return True
