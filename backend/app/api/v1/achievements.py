from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ...db.session import get_db
from ...models.user import User, UserProgressSummary
from ...models.achievements import AchievementProgress
from ...models.game import LevelProgress
from ...api.v1.auth import require_current_user

router = APIRouter()

ACHIEVEMENTS_DEF = [
    {
        "id": "first_win",
        "title": "First Win",
        "description": "Complete Level 1",
        "icon": "🏆",
        "target": 1,
        "reward_coins": 50
    },
    {
        "id": "level_10",
        "title": "Complete Level 10",
        "description": "Reach and clear Level 10",
        "icon": "🏅",
        "target": 10,
        "reward_coins": 100
    },
    {
        "id": "level_25",
        "title": "Complete Level 25",
        "description": "Reach and clear Level 25",
        "icon": "🌟",
        "target": 25,
        "reward_coins": 250
    },
    {
        "id": "level_50",
        "title": "Complete Level 50",
        "description": "Master all 50 levels of Arrow Escape",
        "icon": "👑",
        "target": 50,
        "reward_coins": 500
    },
    {
        "id": "coins_100",
        "title": "Earn 100 Coins",
        "description": "Collect a total of 100 coins",
        "icon": "💰",
        "target": 100,
        "reward_coins": 50
    },
    {
        "id": "coins_1000",
        "title": "Earn 1000 Coins",
        "description": "Collect a total of 1000 coins",
        "icon": "💎",
        "target": 1000,
        "reward_coins": 200
    },
    {
        "id": "three_star_all",
        "title": "3 Star Master",
        "description": "Earn 3 stars on 10 levels",
        "icon": "⭐",
        "target": 10,
        "reward_coins": 300
    },
    {
        "id": "no_heart_loss",
        "title": "Finish Without Losing Hearts",
        "description": "Clear a level with full hearts intact",
        "icon": "❤️",
        "target": 1,
        "reward_coins": 100
    },
    {
        "id": "speed_runner",
        "title": "Speed Runner",
        "description": "Complete any level in under 10 seconds",
        "icon": "⚡",
        "target": 1,
        "reward_coins": 150
    },
    {
        "id": "collector",
        "title": "Star Collector",
        "description": "Earn 30 total stars across all levels",
        "icon": "🎒",
        "target": 30,
        "reward_coins": 200
    }
]

class ClaimRequest(BaseModel):
    achievement_id: str

class SyncAchievementItem(BaseModel):
    id: str
    progress: int

class SyncAchievementsRequest(BaseModel):
    achievements: List[SyncAchievementItem]

@router.get('', response_model=List[Dict[str, Any]])
def get_achievements(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    user_progs = db.query(AchievementProgress).filter(AchievementProgress.user_id == user.id).all()
    prog_map = {p.achievement_id: p for p in user_progs}
    
    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
    user_levels = db.query(LevelProgress).filter(LevelProgress.user_id == user.id, LevelProgress.completed == True).all()

    # Dynamic progression calculation
    calc_map = {
        "first_win": 1 if (summary and summary.completed_levels >= 1) else 0,
        "level_10": summary.highest_unlocked_level - 1 if summary else 0,
        "level_25": summary.highest_unlocked_level - 1 if summary else 0,
        "level_50": summary.highest_unlocked_level - 1 if summary else 0,
        "coins_100": summary.total_coins if summary else 0,
        "coins_1000": summary.total_coins if summary else 0,
        "three_star_all": sum(1 for p in user_levels if p.stars == 3),
        "no_heart_loss": 1 if any(p.completed for p in user_levels) else 0,
        "speed_runner": 1 if any(p.best_time > 0 and p.best_time <= 10.0 for p in user_levels) else 0,
        "collector": summary.total_stars if summary else 0
    }

    result = []
    for ach in ACHIEVEMENTS_DEF:
        ach_id = ach["id"]
        p_obj = prog_map.get(ach_id)
        current_p = max(calc_map.get(ach_id, 0), p_obj.progress if p_obj else 0)
        unlocked = (p_obj.unlocked if p_obj else False) or (current_p >= ach["target"])
        claimed = p_obj.claimed if p_obj else False

        result.append({
            "id": ach_id,
            "title": ach["title"],
            "description": ach["description"],
            "icon": ach["icon"],
            "target": ach["target"],
            "progress": min(current_p, ach["target"]),
            "reward_coins": ach["reward_coins"],
            "unlocked": unlocked,
            "claimed": claimed
        })

    return result

@router.post('/claim')
def claim_achievement(req: ClaimRequest, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    ach_def = next((a for a in ACHIEVEMENTS_DEF if a["id"] == req.achievement_id), None)
    if not ach_def:
        raise HTTPException(status_code=404, detail="Achievement not found.")

    p_obj = db.query(AchievementProgress).filter(
        AchievementProgress.user_id == user.id,
        AchievementProgress.achievement_id == req.achievement_id
    ).first()

    if not p_obj or not p_obj.unlocked:
        # Check if user meets unlock criteria now
        summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
        if not summary:
            raise HTTPException(status_code=400, detail="Achievement is not unlocked yet.")
        
        # Unlock if target met
        p_obj = AchievementProgress(
            user_id=user.id,
            achievement_id=req.achievement_id,
            progress=ach_def["target"],
            unlocked=True,
            claimed=False,
            unlocked_at=datetime.utcnow()
        )
        db.add(p_obj)

    if p_obj.claimed:
        raise HTTPException(status_code=400, detail="Reward already claimed.")

    p_obj.claimed = True
    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
    if not summary:
        summary = UserProgressSummary(user_id=user.id)
        db.add(summary)

    summary.total_coins = (summary.total_coins or 0) + ach_def["reward_coins"]
    db.commit()

    return {
        "success": True,
        "achievement_id": req.achievement_id,
        "reward_coins": ach_def["reward_coins"],
        "total_coins": summary.total_coins
    }

@router.post('/sync')
def sync_achievements(req: SyncAchievementsRequest, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    newly_unlocked = []
    for item in req.achievements:
        ach_def = next((a for a in ACHIEVEMENTS_DEF if a["id"] == item.id), None)
        if not ach_def: continue

        p_obj = db.query(AchievementProgress).filter(
            AchievementProgress.user_id == user.id,
            AchievementProgress.achievement_id == item.id
        ).first()

        if not p_obj:
            p_obj = AchievementProgress(
                user_id=user.id,
                achievement_id=item.id,
                progress=0,
                unlocked=False,
                claimed=False
            )
            db.add(p_obj)

        p_obj.progress = max(p_obj.progress or 0, item.progress)
        if not p_obj.unlocked and p_obj.progress >= ach_def["target"]:
            p_obj.unlocked = True
            p_obj.unlocked_at = datetime.utcnow()
            newly_unlocked.append(ach_def)

    db.commit()
    return {"success": True, "newly_unlocked": newly_unlocked}
