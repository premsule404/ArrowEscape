from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime
from ..db.base_class import Base

class CloudSyncQueue(Base):
    __tablename__ = "cloud_sync_queue"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    action = Column(String, nullable=False) # e.g. 'level_complete', 'setting_update'
    payload = Column(Text, nullable=False) # JSON payload
    status = Column(String, default="pending") # 'pending', 'synced', 'failed'
    created_at = Column(DateTime, default=datetime.utcnow)
    synced_at = Column(DateTime, nullable=True)
