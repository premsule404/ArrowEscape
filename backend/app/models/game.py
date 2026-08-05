from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Float
from datetime import datetime
from ..db.base_class import Base

class LevelCategory(Base):
    __tablename__ = "level_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

class LevelPack(Base):
    __tablename__ = "level_packs"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category_id = Column(Integer, ForeignKey("level_categories.id"))

class Level(Base):
    __tablename__ = "levels"
    id = Column(String, primary_key=True)
    pack_id = Column(Integer, ForeignKey("level_packs.id"), nullable=True)
    level_number = Column(Integer, index=True, unique=True)
    name = Column(String)
    difficulty = Column(Integer, default=1)
    base_coins = Column(Integer, default=100)
    width = Column(Integer, default=5)
    height = Column(Integer, default=5)
    published_status = Column(String, default="published")

class Progress(Base):
    __tablename__ = "progress_totals"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    current_level = Column(String)
    highest_level = Column(String)
    total_levels_completed = Column(Integer, default=0)
    total_moves = Column(Integer, default=0)
    total_play_time = Column(Integer, default=0)
    last_played = Column(DateTime)

class LevelProgress(Base):
    __tablename__ = "level_progress"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    level_num = Column(Integer, index=True)
    stars = Column(Integer, default=0)
    best_moves = Column(Integer, default=0)
    best_time = Column(Float, default=0.0)
    coins_claimed = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    unlocked = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DailyChallenge(Base):
    __tablename__ = "daily_challenges"
    id = Column(Integer, primary_key=True)
    challenge_id = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    completed = Column(Boolean, default=False)
    reward_claimed = Column(Boolean, default=False)
    completion_time = Column(DateTime, nullable=True)
