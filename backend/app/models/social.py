from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, DateTime
from datetime import datetime
from ..db.base_class import Base

class Friend(Base):
    __tablename__ = "friends"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    friend_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class FriendRequest(Base):
    __tablename__ = "friend_requests"
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), index=True)
    receiver_id = Column(Integer, ForeignKey("users.id"), index=True)
    status = Column(String, default="pending", index=True) # "pending", "accepted", "rejected"
    created_at = Column(DateTime, default=datetime.utcnow)

class PlayerBlock(Base):
    __tablename__ = "player_blocks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    blocked_id = Column(Integer, ForeignKey("users.id"), index=True)

class CommunityLevel(Base):
    __tablename__ = "community_levels"
    id = Column(String, primary_key=True)
    creator_id = Column(Integer, ForeignKey("users.id"))
    json_data = Column(Text)
    downloads = Column(Integer, default=0)

class LevelRating(Base):
    __tablename__ = "level_ratings"
    id = Column(Integer, primary_key=True)
    level_id = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    rating = Column(Float)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    level_id = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)

class PlayerReport(Base):
    __tablename__ = "player_reports"
    id = Column(Integer, primary_key=True)
    reporter_id = Column(Integer, ForeignKey("users.id"))
    reported_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(Text)
