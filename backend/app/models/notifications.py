from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from ..db.base_class import Base

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String) 
    content = Column(String)
    read = Column(Boolean, default=False)
