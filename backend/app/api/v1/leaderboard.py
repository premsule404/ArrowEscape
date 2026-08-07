from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Dict, Any, Optional

from ...db.session import get_db
from ...models.user import User, PlayerProfile, UserProgressSummary
from ...models.game import LevelProgress
from ...api.v1.auth import get_current_user_optional

router = APIRouter()

@router.get('', response_model=List[Dict[str, Any]])
def get_leaderboard(
    category: str = Query("stars", description="stars, coins, levels, or speed"),
    scope: str = Query("global", description="global, country, or friends"),
    timeframe: str = Query("all_time", description="all_time, monthly, or weekly"),
    limit: int = Query(50, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    query = db.query(UserProgressSummary, PlayerProfile, User).join(
        PlayerProfile, UserProgressSummary.user_id == PlayerProfile.user_id
    ).join(
        User, UserProgressSummary.user_id == User.id
    )

    # Scope filtering
    if scope == "country" and current_user:
        user_prof = db.query(PlayerProfile).filter(PlayerProfile.user_id == current_user.id).first()
        if user_prof and user_prof.country:
            query = query.filter(PlayerProfile.country == user_prof.country)
    
    # Sorting
    if category == "coins":
        query = query.order_by(desc(UserProgressSummary.total_coins))
    elif category == "levels":
        query = query.order_by(desc(UserProgressSummary.completed_levels))
    else:
        query = query.order_by(desc(UserProgressSummary.total_stars))
        
    results = query.limit(limit).all()
    
    leaderboard_data = []
    for rank, (summary, profile, user) in enumerate(results, 1):
        completed_cnt = summary.completed_levels or 0
        completion_pct = round((completed_cnt / 50.0) * 100, 1) if completed_cnt > 0 else 0.0

        # Calculate fastest time for user across completed levels
        best_time_res = db.query(func.min(LevelProgress.best_time)).filter(
            LevelProgress.user_id == user.id,
            LevelProgress.completed == True,
            LevelProgress.best_time > 0
        ).scalar()
        fastest_time = round(float(best_time_res), 1) if best_time_res else 0.0

        leaderboard_data.append({
            "rank": rank,
            "user_id": user.id,
            "username": user.username,
            "display_name": profile.display_name or user.username,
            "avatar": profile.avatar or "🎯",
            "country": profile.country or "Global",
            "total_stars": summary.total_stars or 0,
            "total_coins": summary.total_coins or 0,
            "completed_levels": completed_cnt,
            "completion_pct": completion_pct,
            "fastest_time": fastest_time,
            "is_current_user": bool(current_user and current_user.id == user.id)
        })
        
    return leaderboard_data
