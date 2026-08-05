from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from ..db.base_class import Base

class AdminUser(Base):
    __tablename__ = "admin_users"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String)

class BanHistory(Base):
    __tablename__ = "ban_history"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    admin_id = Column(Integer, ForeignKey("admin_users.id"))
    reason = Column(Text)
    banned_until = Column(DateTime)

class SystemLog(Base):
    __tablename__ = "system_logs"
    id = Column(Integer, primary_key=True)
    level = Column(String) 
    message = Column(Text)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"))
    action = Column(String)
    target_id = Column(String)
