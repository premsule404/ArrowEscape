from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.user import User, PlayerProfile, UserProgressSummary
from ...models.game import LevelProgress
from ...repositories.player_repo import PlayerRepository
from ...api.v1.auth import require_current_user
from ...core.security import verify_password, get_password_hash
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ProfileUpdateSchema(BaseModel):
    username: Optional[str] = None
    display_name: Optional[str] = None
    country: Optional[str] = None
    preferred_language: Optional[str] = None
    theme: Optional[str] = None
    avatar: Optional[str] = None
    sound_enabled: Optional[bool] = None
    music_enabled: Optional[bool] = None

class ChangePasswordSchema(BaseModel):
    old_password: str
    new_password: str

@router.get('')
def get_profile(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    repo = PlayerRepository(db)
    profile = repo.get_profile(user.id)
    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
    
    progress_records = db.query(LevelProgress).filter(LevelProgress.user_id == user.id, LevelProgress.completed == True).all()
    valid_times = [p.best_time for p in progress_records if p.best_time and p.best_time > 0]
    valid_scores = [p.best_moves for p in progress_records if p.best_moves and p.best_moves > 0]
    
    best_time = min(valid_times) if valid_times else 0.0
    best_score = min(valid_scores) if valid_scores else 0
    
    completed_cnt = summary.completed_levels if summary else 0
    completion_pct = round((completed_cnt / 50.0) * 100, 1) if completed_cnt > 0 else 0.0

    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email or "N/A",
        "is_guest": user.is_guest,
        "display_name": profile.display_name if profile else user.username,
        "avatar": (profile.avatar if profile and profile.avatar else "🎯"),
        "country": profile.country if profile else "Global",
        "theme": profile.theme if profile else "default",
        "total_coins": summary.total_coins if summary else 0,
        "total_stars": summary.total_stars if summary else 0,
        "current_level": summary.current_level if summary else 1,
        "highest_level": summary.highest_unlocked_level if summary else 1,
        "games_played": summary.games_played if summary else 0,
        "games_won": completed_cnt,
        "completion_pct": completion_pct,
        "best_time": best_time,
        "best_score": best_score,
        "date_joined": user.created_at.strftime("%Y-%m-%d") if user.created_at else "N/A",
        "last_login": user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "N/A"
    }

@router.patch('')
def update_profile(data: ProfileUpdateSchema, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    repo = PlayerRepository(db)
    
    if data.username and data.username != user.username:
        existing = db.query(User).filter(User.username == data.username, User.id != user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username is already taken.")
        user.username = data.username
        db.commit()

    updated = repo.update_profile(user.id, **data.model_dump(exclude_unset=True))
    return {
        "success": True,
        "username": user.username,
        "profile": {
            "user_id": user.id,
            "display_name": updated.display_name,
            "avatar": updated.avatar,
            "country": updated.country,
            "theme": updated.theme
        }
    }

@router.post('/change-password')
def change_password(data: ChangePasswordSchema, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    if not user.password_hash or not verify_password(data.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect current password.")
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters.")
    user.password_hash = get_password_hash(data.new_password)
    db.commit()
    return {"success": True, "message": "Password updated successfully."}

@router.delete('')
def delete_account(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    db.query(PlayerProfile).filter(PlayerProfile.user_id == user.id).delete()
    db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).delete()
    db.query(LevelProgress).filter(LevelProgress.user_id == user.id).delete()
    db.delete(user)
    db.commit()
    return {"success": True, "message": "Account deleted successfully."}
