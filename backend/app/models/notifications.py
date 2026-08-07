from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from datetime import datetime
from ..db.base_class import Base

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    type = Column(String, index=True)
    title = Column(String, nullable=True)
    content = Column(String, nullable=False)
    icon = Column(String, default="🔔")
    read = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
