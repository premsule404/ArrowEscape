from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...db.session import get_db
from ...models.user import User, PlayerProfile, UserProgressSummary
from ...models.game import LevelProgress, Level
from ...schemas.progress import CloudSyncRequest, CloudSyncResponse
from ...api.v1.auth import require_current_user

router = APIRouter()

def calculate_coin_reward(stars: int, base_coins: int = 100) -> int:
    if stars == 3: return base_coins
    elif stars == 2: return int(base_coins * 0.70)
    elif stars == 1: return int(base_coins * 0.50)
    return 0

@router.get('', response_model=dict)
def get_progress(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
    progress_records = db.query(LevelProgress).filter(LevelProgress.user_id == user.id).all()
    
    levels_data = []
    for p in progress_records:
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
        "total_coins": summary.total_coins if summary else 0,
        "total_stars": summary.total_stars if summary else 0,
        "completed_count": summary.completed_levels if summary else 0,
        "current_level": summary.current_level if summary else 1,
        "highest_unlocked_level": summary.highest_unlocked_level if summary else 1,
        "levels": levels_data
    }

@router.post('/sync', response_model=CloudSyncResponse)
def sync_progress(sync_req: CloudSyncRequest, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
    if not summary:
        summary = UserProgressSummary(user_id=user.id)
        db.add(summary)
        db.commit()
        db.refresh(summary)
        
    profile = db.query(PlayerProfile).filter(PlayerProfile.user_id == user.id).first()
    if profile:
        if sync_req.theme: profile.theme = sync_req.theme
        if sync_req.color_tutorial_dismissed is not None: profile.color_tutorial_dismissed = sync_req.color_tutorial_dismissed
        
    for item in sync_req.levels:
        lvl = db.query(LevelProgress).filter(
            LevelProgress.user_id == user.id,
            LevelProgress.level_num == item.level_id
        ).first()
        
        if not lvl:
            lvl = LevelProgress(
                user_id=user.id,
                level_num=item.level_id,
                stars=0,
                coins_claimed=0,
                best_time=0.0,
                best_moves=0,
                completed=False,
                unlocked=True
            )
            db.add(lvl)
            
        old_stars = lvl.stars or 0
        old_claimed = lvl.coins_claimed or 0
        old_time = lvl.best_time or 0.0
        
        new_stars = max(old_stars, item.stars or 0)
        new_claimed = max(old_claimed, calculate_coin_reward(new_stars, item.base_coins))
        new_time = item.time if (old_time == 0 or item.time < old_time) else old_time
        
        inc_stars = max(0, new_stars - old_stars)
        inc_coins = max(0, new_claimed - old_claimed)
        
        lvl.stars = new_stars
        lvl.coins_claimed = new_claimed
        lvl.best_moves = item.moves
        lvl.best_time = new_time
        lvl.completed = lvl.completed or item.completed
        lvl.attempts = (lvl.attempts or 0) + 1
        
        summary.total_stars = (summary.total_stars or 0) + inc_stars
        summary.total_coins = (summary.total_coins or 0) + inc_coins
        
    db.commit()
    
    user_levels = db.query(LevelProgress).filter(LevelProgress.user_id == user.id).all()
    completed_cnt = sum(1 for p in user_levels if p.completed)
    summary.completed_levels = completed_cnt
    
    max_completed = max([p.level_num for p in user_levels if p.completed], default=0)
    summary.highest_unlocked_level = min(50, max(1, max_completed + 1))
    
    if sync_req.current_level:
        summary.current_level = sync_req.current_level
    else:
        summary.current_level = summary.highest_unlocked_level
        
    db.commit()
    
    all_levels = []
    for p in user_levels:
        all_levels.append({
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
        "levels": all_levels
    }
