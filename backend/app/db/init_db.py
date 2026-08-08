import os
import json
from sqlalchemy.orm import Session
from .base_class import Base
from .session import engine
from ..models.user import User, PlayerProfile, UserProgressSummary, Settings
from ..models.game import Level
from ..core.security import get_password_hash

from sqlalchemy import text

def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Lightweight auto-migrations for SQLite
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE notifications ADD COLUMN title VARCHAR"))
            conn.commit()
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE notifications ADD COLUMN icon VARCHAR"))
            conn.commit()
        except Exception:
            pass

    db = Session(bind=engine)
    try:
        # Populate levels 1 to 50 if missing
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        levels_dir = os.path.join(root_dir, "levels")
        
        if os.path.exists(levels_dir):
            for level_num in range(1, 51):
                level_file = os.path.join(levels_dir, f"level{level_num:03d}.json")
                if os.path.exists(level_file):
                    with open(level_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    existing = db.query(Level).filter(Level.level_number == level_num).first()
                    if not existing:
                        lvl = Level(
                            id=data.get("id", f"level{level_num:03d}"),
                            level_number=level_num,
                            name=data.get("name", f"Level {level_num}"),
                            difficulty=data.get("difficulty", 1),
                            base_coins=data.get("rewards", {}).get("coins", 100),
                            width=data.get("grid", {}).get("width", 5),
                            height=data.get("grid", {}).get("height", 5),
                            published_status="published"
                        )
                        db.add(lvl)
            db.commit()
            
        # Create default admin account if not exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@arrowescape.com",
                password_hash=get_password_hash("admin123"),
                is_admin=True,
                is_guest=False
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            profile = PlayerProfile(user_id=admin_user.id, display_name="Admin Boss", country="Global")
            summary = UserProgressSummary(user_id=admin_user.id, total_coins=9999, total_stars=150)
            settings = Settings(user_id=admin_user.id)
            db.add(profile)
            db.add(summary)
            db.add(settings)
            db.commit()
            
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
