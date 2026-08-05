from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: Optional[str] = None
    password: Optional[str] = None
    is_guest: bool = False

class UserLogin(BaseModel):
    username: str
    password: str

class GuestLogin(BaseModel):
    device_id: Optional[str] = None
    display_name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    avatar: Optional[str] = None
    country: Optional[str] = None
    preferred_language: str = "en"
    theme: str = "default"
    is_guest: bool = False
    is_admin: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    total_coins: int = 0
    total_stars: int = 0
    completed_levels: int = 0
    current_level: int = 1

class UserSettingsUpdate(BaseModel):
    display_name: Optional[str] = None
    country: Optional[str] = None
    theme: Optional[str] = None
    avatar: Optional[str] = None
    sound_enabled: Optional[bool] = None
    music_enabled: Optional[bool] = None
    vibration_enabled: Optional[bool] = None
    preferred_language: Optional[str] = None
