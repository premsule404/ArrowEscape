from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from ...db.session import get_db
from ...models.user import User, UserProgressSummary
from ...models.daily import UserDailyReward
from ...api.v1.auth import require_current_user

router = APIRouter()

DAILY_REWARDS = [
    {"day": 1, "coins": 50, "stars": 0, "bonus": False, "label": "Day 1"},
    {"day": 2, "coins": 100, "stars": 0, "bonus": False, "label": "Day 2"},
    {"day": 3, "coins": 150, "stars": 0, "bonus": False, "label": "Day 3"},
    {"day": 4, "coins": 200, "stars": 0, "bonus": False, "label": "Day 4"},
    {"day": 5, "coins": 250, "stars": 0, "bonus": False, "label": "Day 5"},
    {"day": 6, "coins": 300, "stars": 0, "bonus": False, "label": "Day 6"},
    {"day": 7, "coins": 500, "stars": 5, "bonus": True, "label": "Weekly Bonus!"}
]

MONTHLY_BONUS_REQUIREMENT = 28
MONTHLY_BONUS_COINS = 2000
MONTHLY_BONUS_STARS = 10

def get_user_daily_record(user_id: int, db: Session) -> UserDailyReward:
    record = db.query(UserDailyReward).filter(UserDailyReward.user_id == user_id).first()
    if not record:
        record = UserDailyReward(user_id=user_id, streak_count=0, total_claims=0, last_claim_date=None)
        db.add(record)
        db.commit()
        db.refresh(record)
    return record

@router.get('/status', response_model=Dict[str, Any])
def get_daily_status(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    record = get_user_daily_record(user.id, db)
    now = datetime.now(timezone.utc)
    
    last_date = record.last_claim_date.replace(tzinfo=timezone.utc) if record.last_claim_date else None
    
    can_claim = False
    next_day_streak = record.streak_count or 0

    if not last_date:
        can_claim = True
        next_day_streak = 1
    else:
        days_diff = (now.date() - last_date.date()).days
        if days_diff == 0:
            can_claim = False
            next_day_streak = record.streak_count
        elif days_diff == 1:
            can_claim = True
            next_day_streak = (record.streak_count % 7) + 1
        else:
            # Missed Day handling: streak resets to 1
            can_claim = True
            next_day_streak = 1

    # Calculate seconds until next UTC midnight
    tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_remaining = int((tomorrow - now).total_seconds())

    return {
        "can_claim": can_claim,
        "current_streak": record.streak_count,
        "next_streak_day": next_day_streak,
        "total_claims": record.total_claims,
        "seconds_to_next_reset": seconds_remaining if not can_claim else 0,
        "rewards": DAILY_REWARDS,
        "monthly_bonus": {
            "requirement": MONTHLY_BONUS_REQUIREMENT,
            "coins": MONTHLY_BONUS_COINS,
            "stars": MONTHLY_BONUS_STARS,
            "progress": record.total_claims % MONTHLY_BONUS_REQUIREMENT,
            "eligible": (record.total_claims > 0 and record.total_claims % MONTHLY_BONUS_REQUIREMENT == 0 and can_claim)
        }
    }

@router.post('/claim')
def claim_daily_reward(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    record = get_user_daily_record(user.id, db)
    now = datetime.now(timezone.utc)
    
    last_date = record.last_claim_date.replace(tzinfo=timezone.utc) if record.last_claim_date else None

    if last_date and (now.date() - last_date.date()).days == 0:
        raise HTTPException(status_code=400, detail="Daily reward already claimed today. Try again tomorrow!")

    days_diff = (now.date() - last_date.date()).days if last_date else 1

    if days_diff == 1:
        new_streak = (record.streak_count % 7) + 1
    else:
        # Streak resets to 1 if > 1 day elapsed
        new_streak = 1

    record.streak_count = new_streak
    record.total_claims = (record.total_claims or 0) + 1
    record.last_claim_date = now.replace(tzinfo=None)

    # Calculate Reward
    reward_item = DAILY_REWARDS[new_streak - 1]
    earned_coins = reward_item["coins"]
    earned_stars = reward_item["stars"]

    # Monthly Bonus check
    monthly_claimed = False
    if record.total_claims % MONTHLY_BONUS_REQUIREMENT == 0:
        earned_coins += MONTHLY_BONUS_COINS
        earned_stars += MONTHLY_BONUS_STARS
        monthly_claimed = True

    # Update User Progress Summary
    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
    if not summary:
        summary = UserProgressSummary(user_id=user.id)
        db.add(summary)

    summary.total_coins = (summary.total_coins or 0) + earned_coins
    summary.total_stars = (summary.total_stars or 0) + earned_stars
    db.commit()

    return {
        "success": True,
        "streak_day": new_streak,
        "earned_coins": earned_coins,
        "earned_stars": earned_stars,
        "weekly_bonus_applied": reward_item["bonus"],
        "monthly_bonus_applied": monthly_claimed,
        "total_coins": summary.total_coins,
        "total_stars": summary.total_stars,
        "total_claims": record.total_claims
    }
