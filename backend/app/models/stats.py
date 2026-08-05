from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from ..db.base_class import Base

class Statistics(Base):
    __tablename__ = "statistics"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    games_started = Column(Integer, default=0)
    games_finished = Column(Integer, default=0)
    total_restarts = Column(Integer, default=0)
    total_undos = Column(Integer, default=0)
    total_hints_used = Column(Integer, default=0)
    average_moves_per_level = Column(Float, default=0.0)
    average_completion_time = Column(Float, default=0.0)
    longest_play_session = Column(Integer, default=0)
    shortest_completion = Column(Integer, default=0)
    win_percentage = Column(Float, default=0.0)

class AdvancedPlayerAnalytics(Base):
    __tablename__ = "advanced_analytics"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    favorite_theme = Column(String)
    favorite_game_mode = Column(String)
    first_login = Column(DateTime)
    last_login = Column(DateTime)
    consecutive_login_days = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    highest_streak = Column(Integer, default=0)
    total_sessions = Column(Integer, default=0)
    average_session_length = Column(Float, default=0.0)
    total_clicks = Column(Integer, default=0)
    arrows_removed = Column(Integer, default=0)
    failed_attempts = Column(Integer, default=0)
    perfect_levels = Column(Integer, default=0)
    no_hint_levels = Column(Integer, default=0)
    no_undo_levels = Column(Integer, default=0)
    fastest_level_id = Column(String)
    slowest_level_id = Column(String)
