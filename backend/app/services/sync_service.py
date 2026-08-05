from sqlalchemy.orm import Session
from typing import Dict, Any
from ..repositories.progress_repo import ProgressRepository
from ..repositories.player_repo import PlayerRepository
from ..schemas.progress import CloudSyncRequest, CloudSyncResponse

def calculate_coin_reward(stars: int, base_coins: int = 100) -> int:
    if stars == 3: return base_coins
    elif stars == 2: return int(base_coins * 0.70)
    elif stars == 1: return int(base_coins * 0.50)
    return 0

class SyncService:
    def __init__(self, db: Session):
        self.db = db
        self.progress_repo = ProgressRepository(db)
        self.player_repo = PlayerRepository(db)

    def sync_user_progress(self, user_id: int, sync_req: CloudSyncRequest) -> Dict[str, Any]:
        summary = self.progress_repo.get_or_create_summary(user_id)
        
        # Newest Timestamp Wins for Settings & Theme preferences
        if sync_req.theme or sync_req.color_tutorial_dismissed is not None:
            self.player_repo.update_profile(
                user_id,
                theme=sync_req.theme,
                color_tutorial_dismissed=sync_req.color_tutorial_dismissed
            )

        # Highest Progress Wins for Levels, Stars, Coins, Times, Moves
        for item in sync_req.levels:
            lvl = self.progress_repo.get_level_progress(user_id, item.level_id)
            old_stars = lvl.stars if lvl else 0
            old_claimed = lvl.coins_claimed if lvl else 0
            
            new_stars = max(old_stars, item.stars or 0)
            new_claimed = max(old_claimed, calculate_coin_reward(new_stars, item.base_coins))
            
            inc_stars = max(0, new_stars - old_stars)
            inc_coins = max(0, new_claimed - old_claimed)
            
            self.progress_repo.update_level_progress(
                user_id=user_id,
                level_num=item.level_id,
                stars=new_stars,
                moves=item.moves,
                time_taken=item.time,
                coins_claimed=new_claimed,
                completed=item.completed
            )
            
            summary.total_stars = (summary.total_stars or 0) + inc_stars
            summary.total_coins = (summary.total_coins or 0) + inc_coins

        all_levels = self.progress_repo.get_all_level_progress(user_id)
        completed_cnt = sum(1 for p in all_levels if p.completed)
        summary.completed_levels = completed_cnt
        
        max_completed = max([p.level_num for p in all_levels if p.completed], default=0)
        summary.highest_unlocked_level = min(50, max(1, max_completed + 1))
        
        if sync_req.current_level:
            summary.current_level = sync_req.current_level
        else:
            summary.current_level = summary.highest_unlocked_level
            
        self.db.commit()
        
        levels_data = []
        for p in all_levels:
            levels_data.append({
                "level_num": p.level_num,
                "stars": p.stars or 0,
                "best_moves": p.best_moves or 0,
                "best_time": p.best_time or 0.0,
                "coins_claimed": p.coins_claimed or 0,
                "completed": p.completed or False,
                "unlocked": p.unlocked or False
            })
            
        return {
            "success": True,
            "total_coins": summary.total_coins or 0,
            "total_stars": summary.total_stars or 0,
            "completed_count": summary.completed_levels or 0,
            "highest_unlocked_level": summary.highest_unlocked_level or 1,
            "levels": levels_data
        }
