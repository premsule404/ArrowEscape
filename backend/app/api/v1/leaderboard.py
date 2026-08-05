from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Dict, Any

from ...db.session import get_db
from ...models.user import User, PlayerProfile, UserProgressSummary

router = APIRouter()

@router.get('', response_model=List[Dict[str, Any]])
def get_leaderboard(
    category: str = Query("stars", description="stars or coins or levels"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(UserProgressSummary, PlayerProfile, User).join(
        PlayerProfile, UserProgressSummary.user_id == PlayerProfile.user_id
    ).join(
        User, UserProgressSummary.user_id == User.id
    )
    
    if category == "coins":
        query = query.order_by(desc(UserProgressSummary.total_coins))
    elif category == "levels":
        query = query.order_by(desc(UserProgressSummary.completed_levels))
    else:
        query = query.order_by(desc(UserProgressSummary.total_stars))
        
    results = query.limit(limit).all()
    
    leaderboard_data = []
    for rank, (summary, profile, user) in enumerate(results, 1):
        leaderboard_data.append({
            "rank": rank,
            "user_id": user.id,
            "username": user.username,
            "display_name": profile.display_name or user.username,
            "country": profile.country or "Global",
            "avatar": profile.avatar,
            "total_stars": summary.total_stars,
            "total_coins": summary.total_coins,
            "completed_levels": summary.completed_levels,
            "current_level": summary.current_level
        })
        
    return leaderboard_data
