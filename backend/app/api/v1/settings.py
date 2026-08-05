from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...db.session import get_db
from ...models.user import User
from ...repositories.player_repo import PlayerRepository
from ...api.v1.auth import require_current_user
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class SettingsUpdateSchema(BaseModel):
    music_volume: Optional[float] = None
    sfx_volume: Optional[float] = None
    brightness: Optional[float] = None
    language: Optional[str] = None
    fps_limit: Optional[int] = None
    graphics_quality: Optional[str] = None

@router.get('')
def get_settings(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    repo = PlayerRepository(db)
    st = repo.get_settings(user.id)
    return {
        "user_id": user.id,
        "music_volume": st.music_volume if st else 1.0,
        "sfx_volume": st.sfx_volume if st else 1.0,
        "brightness": st.brightness if st else 1.0,
        "language": st.language if st else "en",
        "fps_limit": st.fps_limit if st else 60,
        "graphics_quality": st.graphics_quality if st else "high"
    }

@router.patch('')
def update_settings(data: SettingsUpdateSchema, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    repo = PlayerRepository(db)
    st = repo.update_settings(user.id, **data.model_dump(exclude_unset=True))
    return {
        "success": True,
        "settings": {
            "user_id": user.id,
            "music_volume": st.music_volume,
            "sfx_volume": st.sfx_volume,
            "fps_limit": st.fps_limit,
            "graphics_quality": st.graphics_quality
        }
    }
