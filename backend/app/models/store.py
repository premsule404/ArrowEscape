from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from datetime import datetime
from ..db.base_class import Base

class Inventory(Base):
    __tablename__ = "inventories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    item_type = Column(String, index=True) # e.g. 'coins', 'hints', 'theme_dark'
    quantity = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CoinTransaction(Base):
    __tablename__ = "coin_transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    amount = Column(Integer, nullable=False) # Positive for reward, negative for spend
    source = Column(String, nullable=False) # e.g. 'level_reward', 'admin_grant', 'hint_purchase'
    balance_after = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class HintTransaction(Base):
    __tablename__ = "hint_transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    level_num = Column(Integer, nullable=False)
    cost = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)
