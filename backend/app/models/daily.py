from sqlalchemy import Column, Integer, DateTime, ForeignKey
from datetime import datetime
from ..db.base_class import Base

class UserDailyReward(Base):
    __tablename__ = "user_daily_rewards"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    streak_count = Column(Integer, default=0)
    total_claims = Column(Integer, default=0)
    last_claim_date = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
