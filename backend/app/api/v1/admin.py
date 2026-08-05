from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ...db.session import get_db
from ...models.user import User, PlayerProfile, UserProgressSummary
from ...models.game import LevelProgress
from ...api.v1.auth import require_current_user

router = APIRouter()

def require_admin_user(user: User = Depends(require_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return user

@router.get('/players', response_model=List[Dict[str, Any]])
def list_players(admin: User = Depends(require_admin_user), db: Session = Depends(get_db)):
    users = db.query(User).all()
    players_data = []
    for u in users:
        profile = db.query(PlayerProfile).filter(PlayerProfile.user_id == u.id).first()
        summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == u.id).first()
        players_data.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "display_name": profile.display_name if profile else u.username,
            "country": profile.country if profile else "Global",
            "is_guest": u.is_guest,
            "is_admin": u.is_admin,
            "account_status": u.account_status,
            "total_coins": summary.total_coins if summary else 0,
            "total_stars": summary.total_stars if summary else 0,
            "completed_levels": summary.completed_levels if summary else 0
        })
    return players_data

@router.post('/players/{user_id}/status')
def update_player_status(user_id: int, status_in: Dict[str, str], admin: User = Depends(require_admin_user), db: Session = Depends(get_db)):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Player not found")
    new_status = status_in.get("status", "active")
    u.account_status = new_status
    db.commit()
    return {"message": f"Player {u.username} status updated to {new_status}"}

@router.post('/players/{user_id}/reset')
def reset_player_progress(user_id: int, admin: User = Depends(require_admin_user), db: Session = Depends(get_db)):
    db.query(LevelProgress).filter(LevelProgress.user_id == user_id).delete()
    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user_id).first()
    if summary:
        summary.total_coins = 0
        summary.total_stars = 0
        summary.completed_levels = 0
        summary.current_level = 1
        summary.highest_unlocked_level = 1
    db.commit()
    return {"message": f"Player progress reset successfully"}
