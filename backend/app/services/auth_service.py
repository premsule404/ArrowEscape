import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..repositories.player_repo import PlayerRepository
from ..repositories.progress_repo import ProgressRepository
from ..repositories.auth_repo import AuthRepository
from ..models.user import User, PlayerProfile, UserProgressSummary, Settings
from ..core.security import get_password_hash, verify_password, create_access_token

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.player_repo = PlayerRepository(db)
        self.progress_repo = ProgressRepository(db)
        self.auth_repo = AuthRepository(db)

    def create_guest_account(self, display_name: str = None) -> dict:
        guest_uuid = uuid.uuid4().hex[:8]
        username = f"guest_{guest_uuid}"
        
        user = User(
            username=username,
            email=None,
            password_hash=None,
            is_guest=True,
            is_admin=False
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        profile = PlayerProfile(user_id=user.id, display_name=display_name or f"Guest {guest_uuid}")
        summary = UserProgressSummary(user_id=user.id, current_level=1, highest_unlocked_level=1)
        settings = Settings(user_id=user.id)
        
        self.db.add(profile)
        self.db.add(summary)
        self.db.add(settings)
        self.db.commit()
        
        access_token = create_access_token({"sub": str(user.id), "username": user.username, "is_guest": True})
        refresh_token_obj = self.auth_repo.create_refresh_token(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_obj.token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "is_guest": True
        }

    def register_user(self, username: str, password: str, email: str = None, display_name: str = None) -> dict:
        existing_user = self.player_repo.get_by_username(username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username is already taken.")
            
        user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            is_guest=False,
            is_admin=False
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        profile = PlayerProfile(user_id=user.id, display_name=display_name or username)
        summary = UserProgressSummary(user_id=user.id, current_level=1, highest_unlocked_level=1)
        settings = Settings(user_id=user.id)
        
        self.db.add(profile)
        self.db.add(summary)
        self.db.add(settings)
        self.db.commit()
        
        ev = self.auth_repo.create_email_verification(user.id)
        access_token = create_access_token({"sub": str(user.id), "username": user.username, "is_guest": False})
        refresh_token_obj = self.auth_repo.create_refresh_token(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_obj.token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "is_guest": False,
            "verification_token": ev.token
        }

    def login_user(self, username: str, password: str, ip_address: str = None, user_agent: str = None) -> dict:
        user = self.player_repo.get_by_username(username)
        if not user or not user.password_hash or not verify_password(password, user.password_hash):
            if user:
                self.auth_repo.log_session(user.id, ip_address, user_agent, success=False)
            raise HTTPException(status_code=401, detail="Invalid username or password.")
            
        user.last_login = datetime.utcnow()
        self.db.commit()
        self.auth_repo.log_session(user.id, ip_address, user_agent, success=True)
        
        access_token = create_access_token({"sub": str(user.id), "username": user.username, "is_guest": user.is_guest})
        refresh_token_obj = self.auth_repo.create_refresh_token(user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_obj.token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "is_guest": user.is_guest
        }

    def upgrade_guest_account(self, guest_user_id: int, username: str, password: str, email: str = None) -> dict:
        guest_user = self.player_repo.get_by_id(guest_user_id)
        if not guest_user or not guest_user.is_guest:
            raise HTTPException(status_code=400, detail="User is not a guest account.")
            
        existing_username = self.player_repo.get_by_username(username)
        if existing_username and existing_username.id != guest_user_id:
            raise HTTPException(status_code=400, detail="Username is already taken.")
            
        guest_user.username = username
        guest_user.email = email
        guest_user.password_hash = get_password_hash(password)
        guest_user.is_guest = False
        self.db.commit()
        
        profile = self.player_repo.get_profile(guest_user_id)
        if profile:
            profile.display_name = username
            self.db.commit()
            
        access_token = create_access_token({"sub": str(guest_user.id), "username": guest_user.username, "is_guest": False})
        refresh_token_obj = self.auth_repo.create_refresh_token(guest_user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_obj.token,
            "token_type": "bearer",
            "user_id": guest_user.id,
            "username": guest_user.username,
            "is_guest": False
        }

    def refresh_access_token(self, refresh_token_str: str) -> dict:
        rt = self.auth_repo.get_refresh_token(refresh_token_str)
        if not rt or rt.expires_at < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Invalid or expired refresh token.")
            
        user = self.player_repo.get_by_id(rt.user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found.")
            
        access_token = create_access_token({"sub": str(user.id), "username": user.username, "is_guest": user.is_guest})
        return {
            "access_token": access_token,
            "refresh_token": rt.token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "is_guest": user.is_guest
        }

    def verify_email(self, token_str: str) -> bool:
        ev = self.auth_repo.get_email_verification(token_str)
        if not ev or ev.verified:
            return False
        ev.verified = True
        self.db.commit()
        return True

    def forgot_password(self, email: str) -> str:
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            # Return dummy token for privacy
            return "reset_token_sent"
        pr = self.auth_repo.create_password_reset(user.id)
        return pr.token

    def reset_password(self, token_str: str, new_password: str) -> bool:
        pr = self.auth_repo.get_password_reset(token_str)
        if not pr or pr.expires_at < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
        user = self.player_repo.get_by_id(pr.user_id)
        if not user:
            raise HTTPException(status_code=400, detail="User not found.")
        user.password_hash = get_password_hash(new_password)
        self.auth_repo.revoke_all_user_tokens(user.id)
        self.db.commit()
        return True
