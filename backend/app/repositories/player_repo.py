from sqlalchemy.orm import Session
from typing import Optional
from ..models.user import User, PlayerProfile, Settings

class PlayerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_profile(self, user_id: int) -> Optional[PlayerProfile]:
        return self.db.query(PlayerProfile).filter(PlayerProfile.user_id == user_id).first()

    def get_settings(self, user_id: int) -> Optional[Settings]:
        return self.db.query(Settings).filter(Settings.user_id == user_id).first()

    def update_profile(self, user_id: int, **kwargs) -> PlayerProfile:
        profile = self.get_profile(user_id)
        if not profile:
            profile = PlayerProfile(user_id=user_id)
            self.db.add(profile)
        for key, val in kwargs.items():
            if val is not None and hasattr(profile, key):
                setattr(profile, key, val)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update_settings(self, user_id: int, **kwargs) -> Settings:
        settings = self.get_settings(user_id)
        if not settings:
            settings = Settings(user_id=user_id)
            self.db.add(settings)
        for key, val in kwargs.items():
            if val is not None and hasattr(settings, key):
                setattr(settings, key, val)
        self.db.commit()
        self.db.refresh(settings)
        return settings
