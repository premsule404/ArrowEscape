from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float
from ..db.base_class import Base

class Friend(Base):
    __tablename__ = "friends"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    friend_id = Column(Integer, ForeignKey("users.id"))

class FriendRequest(Base):
    __tablename__ = "friend_requests"
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending") 

class PlayerBlock(Base):
    __tablename__ = "player_blocks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    blocked_id = Column(Integer, ForeignKey("users.id"))

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
