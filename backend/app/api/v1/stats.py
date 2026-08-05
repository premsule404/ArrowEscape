from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.user import User, UserProgressSummary
from ...schemas.stats import PlayerStatsSchema, PlayerStatsUpdateSchema
from ...api.v1.auth import require_current_user

router = APIRouter()

@router.get('', response_model=dict)
def get_stats(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
    return {
        "user_id": user.id,
        "games_played": summary.games_played if summary else 0,
        "games_won": summary.completed_levels if summary else 0,
        "games_lost": 0,
        "replay_count": 0,
        "undo_count": 0,
        "hints_used": 0,
        "avg_completion_time": 0.0,
        "avg_moves": 0.0,
        "total_arrows_released": 0,
        "total_mistakes": 0,
        "accuracy_pct": 100.0
    }

@router.patch('', response_model=dict)
def update_stats(data: PlayerStatsUpdateSchema, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
    if not summary:
        summary = UserProgressSummary(user_id=user.id)
        db.add(summary)
    
    if data.games_played is not None:
        summary.games_played = data.games_played
        
    db.commit()
    return {"success": True, "user_id": user.id}
