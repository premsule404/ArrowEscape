from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timedelta
import secrets
from ..models.user import User, RefreshToken, PasswordResetToken, EmailVerification, LoginHistory

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_refresh_token(self, user_id: int, expires_days: int = 30) -> RefreshToken:
        token_val = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
        rt = RefreshToken(user_id=user_id, token=token_val, expires_at=expires_at, revoked=False)
        self.db.add(rt)
        self.db.commit()
        self.db.refresh(rt)
        return rt

    def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        return self.db.query(RefreshToken).filter(RefreshToken.token == token, RefreshToken.revoked == False).first()

    def revoke_refresh_token(self, token: str):
        rt = self.get_refresh_token(token)
        if rt:
            rt.revoked = True
            self.db.commit()

    def revoke_all_user_tokens(self, user_id: int):
        tokens = self.db.query(RefreshToken).filter(RefreshToken.user_id == user_id, RefreshToken.revoked == False).all()
        for t in tokens:
            t.revoked = True
        self.db.commit()

    def create_email_verification(self, user_id: int) -> EmailVerification:
        token_val = secrets.token_urlsafe(32)
        ev = EmailVerification(user_id=user_id, token=token_val, verified=False)
        self.db.add(ev)
        self.db.commit()
        self.db.refresh(ev)
        return ev

    def get_email_verification(self, token: str) -> Optional[EmailVerification]:
        return self.db.query(EmailVerification).filter(EmailVerification.token == token).first()

    def create_password_reset(self, user_id: int) -> PasswordResetToken:
        token_val = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=2)
        pr = PasswordResetToken(user_id=user_id, token=token_val, expires_at=expires_at)
        self.db.add(pr)
        self.db.commit()
        self.db.refresh(pr)
        return pr

    def get_password_reset(self, token: str) -> Optional[PasswordResetToken]:
        return self.db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()

    def log_session(self, user_id: int, ip_address: Optional[str] = None, user_agent: Optional[str] = None, success: bool = True) -> LoginHistory:
        lh = LoginHistory(user_id=user_id, ip_address=ip_address or "127.0.0.1", user_agent=user_agent or "Unknown", success=success)
        self.db.add(lh)
        self.db.commit()
        self.db.refresh(lh)
        return lh

    def get_user_sessions(self, user_id: int) -> List[LoginHistory]:
        return self.db.query(LoginHistory).filter(LoginHistory.user_id == user_id).order_by(LoginHistory.id.desc()).limit(20).all()
