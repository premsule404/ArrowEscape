from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from ..db.base_class import Base

class AchievementProgress(Base):
    __tablename__ = "achievement_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    achievement_id = Column(String, index=True)
    progress = Column(Integer, default=0)
    unlocked = Column(Boolean, default=False)
    claimed = Column(Boolean, default=False)
    unlocked_at = Column(DateTime, nullable=True)
