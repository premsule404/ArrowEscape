from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Float
from datetime import datetime
from ..db.base_class import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    password_hash = Column(String, nullable=True)
    is_guest = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    profile_picture = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    account_status = Column(String, default="active") 
    jwt_version = Column(Integer, default=1)

class PlayerProfile(Base):
    __tablename__ = "player_profiles"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    display_name = Column(String, nullable=True)
    country = Column(String, default="Global")
    preferred_language = Column(String, default="en")
    theme = Column(String, default="default")
    avatar = Column(String, nullable=True)
    sound_enabled = Column(Boolean, default=True)
    music_enabled = Column(Boolean, default=True)
    vibration_enabled = Column(Boolean, default=True)
    color_tutorial_dismissed = Column(Boolean, default=False)

class UserProgressSummary(Base):
    __tablename__ = "user_progress_summary"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    total_coins = Column(Integer, default=0)
    total_stars = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    highest_unlocked_level = Column(Integer, default=1)
    completed_levels = Column(Integer, default=0)
    games_played = Column(Integer, default=0)
    perfect_levels = Column(Integer, default=0)
    total_play_time = Column(Float, default=0.0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Settings(Base):
    __tablename__ = "user_settings"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    music_volume = Column(Float, default=1.0)
    sfx_volume = Column(Float, default=1.0)
    brightness = Column(Float, default=1.0)
    language = Column(String, default="en")
    control_preferences = Column(String, default="default")
    accessibility_options = Column(String, default="{}")
    fps_limit = Column(Integer, default=60)
    graphics_quality = Column(String, default="high")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    revoked = Column(Boolean, default=False)

class LoginHistory(Base):
    __tablename__ = "login_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String)
    user_agent = Column(String)
    success = Column(Boolean)

class FailedLoginAttempt(Base):
    __tablename__ = "failed_login_attempts"
    id = Column(Integer, primary_key=True)
    ip_address = Column(String, index=True)
    username_attempted = Column(String)

class DeviceInformation(Base):
    __tablename__ = "device_information"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(String, unique=True)
    device_model = Column(String)
    os_version = Column(String)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True)
    expires_at = Column(DateTime)

class EmailVerification(Base):
    __tablename__ = "email_verifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True)
    verified = Column(Boolean, default=False)
