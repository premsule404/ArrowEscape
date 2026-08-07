from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from ..db.base_class import Base

class Inventory(Base):
    __tablename__ = "inventories"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    item_type = Column(String, index=True) # e.g. 'theme_cyberpunk', 'skin_golden', 'hints'
    quantity = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EquippedItems(Base):
    __tablename__ = "equipped_items"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, index=True)
    equipped_theme = Column(String, default="theme_neon")
    equipped_skin = Column(String, default="skin_classic")
    equipped_board = Column(String, default="board_slate")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CoinTransaction(Base):
    __tablename__ = "coin_transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    amount = Column(Integer, nullable=False) # Positive for reward, negative for spend
    source = Column(String, nullable=False) # e.g. 'level_reward', 'shop_purchase'
    balance_after = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class HintTransaction(Base):
    __tablename__ = "hint_transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    level_num = Column(Integer, nullable=False)
    cost = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.utcnow)
