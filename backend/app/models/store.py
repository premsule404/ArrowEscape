from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from ..db.base_class import Base

class Coins(Base):
    __tablename__ = "coins_ledger"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    current_coins = Column(Integer, default=0)
    lifetime_coins = Column(Integer, default=0)
    spent_coins = Column(Integer, default=0)
    earned_from_levels = Column(Integer, default=0)
    earned_from_rewards = Column(Integer, default=0)

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    reward_coins = Column(Integer)

class UserAchievement(Base):
    __tablename__ = "user_achievements"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    achievement_id = Column(String, ForeignKey("achievements.id"))
    unlocked = Column(Boolean, default=False)
    unlocked_date = Column(DateTime)

class Theme(Base):
    __tablename__ = "themes"
    id = Column(String, primary_key=True)
    name = Column(String)
    cost = Column(Integer)
    is_premium = Column(Boolean, default=False)

class UserTheme(Base):
    __tablename__ = "user_themes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    theme_id = Column(String, ForeignKey("themes.id"))
    unlocked = Column(Boolean, default=False)
    equipped = Column(Boolean, default=False)

class Purchase(Base):
    __tablename__ = "purchases"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(String)
    item_type = Column(String)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount_usd = Column(Float)
    coins_purchased = Column(Integer)
    transaction_id = Column(String, unique=True)
