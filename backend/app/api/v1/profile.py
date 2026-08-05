from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.user import User
from ...repositories.player_repo import PlayerRepository
from ...api.v1.auth import require_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ProfileUpdateSchema(BaseModel):
    display_name: Optional[str] = None
    country: Optional[str] = None
    preferred_language: Optional[str] = None
    theme: Optional[str] = None
    avatar: Optional[str] = None
    sound_enabled: Optional[bool] = None
    music_enabled: Optional[bool] = None
    vibration_enabled: Optional[bool] = None
    color_tutorial_dismissed: Optional[bool] = None

@router.get('')
def get_profile(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    repo = PlayerRepository(db)
    profile = repo.get_profile(user.id)
    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_guest": user.is_guest,
        "display_name": profile.display_name if profile else user.username,
        "country": profile.country if profile else "Global",
        "theme": profile.theme if profile else "default",
        "avatar": profile.avatar if profile else None,
        "sound_enabled": profile.sound_enabled if profile else True,
        "music_enabled": profile.music_enabled if profile else True,
        "vibration_enabled": profile.vibration_enabled if profile else True
    }

@router.patch('')
def update_profile(data: ProfileUpdateSchema, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    repo = PlayerRepository(db)
    updated = repo.update_profile(user.id, **data.model_dump(exclude_unset=True))
    return {
        "success": True,
        "profile": {
            "user_id": user.id,
            "display_name": updated.display_name,
            "country": updated.country,
            "theme": updated.theme,
            "sound_enabled": updated.sound_enabled,
            "music_enabled": updated.music_enabled
        }
    }
