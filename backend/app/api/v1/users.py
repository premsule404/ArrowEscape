from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.user import User, PlayerProfile, UserProgressSummary, Settings
from ...schemas.user import UserSettingsUpdate, UserProfileResponse
from ...api.v1.auth import require_current_user

router = APIRouter()

@router.get('/profile', response_model=UserProfileResponse)
def get_profile(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    profile = db.query(PlayerProfile).filter(PlayerProfile.user_id == user.id).first()
    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "display_name": profile.display_name if profile else user.username,
        "avatar": profile.avatar if profile else None,
        "country": profile.country if profile else "Global",
        "preferred_language": profile.preferred_language if profile else "en",
        "theme": profile.theme if profile else "default",
        "is_guest": user.is_guest,
        "is_admin": user.is_admin,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "total_coins": summary.total_coins if summary else 0,
        "total_stars": summary.total_stars if summary else 0,
        "completed_levels": summary.completed_levels if summary else 0,
        "current_level": summary.current_level if summary else 1
    }

@router.put('/settings')
def update_settings(settings_in: UserSettingsUpdate, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    profile = db.query(PlayerProfile).filter(PlayerProfile.user_id == user.id).first()
    if not profile:
        profile = PlayerProfile(user_id=user.id)
        db.add(profile)
        
    if settings_in.display_name is not None: profile.display_name = settings_in.display_name
    if settings_in.country is not None: profile.country = settings_in.country
    if settings_in.theme is not None: profile.theme = settings_in.theme
    if settings_in.avatar is not None: profile.avatar = settings_in.avatar
    if settings_in.sound_enabled is not None: profile.sound_enabled = settings_in.sound_enabled
    if settings_in.music_enabled is not None: profile.music_enabled = settings_in.music_enabled
    if settings_in.vibration_enabled is not None: profile.vibration_enabled = settings_in.vibration_enabled
    if settings_in.preferred_language is not None: profile.preferred_language = settings_in.preferred_language
    
    db.commit()
    return {"message": "Settings updated successfully"}
