from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session
from typing import Optional
from ...db.session import get_db
from ...models.user import User
from ...schemas.auth import (
    RegisterRequestSchema, LoginRequestSchema, GuestLoginRequestSchema, GuestUpgradeRequestSchema,
    TokenResponseSchema, RefreshTokenRequestSchema, EmailVerificationRequestSchema,
    ForgotPasswordRequestSchema, ResetPasswordRequestSchema
)
from ...services.auth_service import AuthService
from ...repositories.player_repo import PlayerRepository
from ...core.security import decode_access_token

router = APIRouter()

def require_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication token required.")
    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired authentication token.")
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    return user

@router.post('/guest', response_model=TokenResponseSchema)
def guest_login(req: GuestLoginRequestSchema, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.create_guest_account(display_name=req.display_name)

@router.post('/register', response_model=TokenResponseSchema)
def register(req: RegisterRequestSchema, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.register_user(
        username=req.username,
        password=req.password,
        email=req.email,
        display_name=req.display_name
    )

@router.post('/login', response_model=TokenResponseSchema)
def login(req: LoginRequestSchema, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    client_ip = request.client.host if request.client else "127.0.0.1"
    user_agent = request.headers.get("user-agent", "Unknown")
    return service.login_user(req.username, req.password, ip_address=client_ip, user_agent=user_agent)

@router.post('/upgrade-guest', response_model=TokenResponseSchema)
def upgrade_guest(req: GuestUpgradeRequestSchema, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.upgrade_guest_account(
        guest_user_id=user.id,
        username=req.username,
        password=req.password,
        email=req.email
    )

@router.post('/refresh', response_model=TokenResponseSchema)
def refresh_token(req: RefreshTokenRequestSchema, db: Session = Depends(get_db)):
    service = AuthService(db)
    return service.refresh_access_token(req.refresh_token)

@router.post('/logout')
def logout(req: RefreshTokenRequestSchema, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.auth_repo.revoke_refresh_token(req.refresh_token)
    return {"success": True, "message": "Logged out successfully."}

@router.post('/google', response_model=TokenResponseSchema)
def google_login(db: Session = Depends(get_db)):
    # OAuth 2.0 Integration Endpoint Stub
    service = AuthService(db)
    return service.create_guest_account(display_name="Google Player")

@router.post('/verify-email')
def verify_email(req: EmailVerificationRequestSchema, db: Session = Depends(get_db)):
    service = AuthService(db)
    success = service.verify_email(req.token)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
    return {"success": True, "message": "Email verified successfully."}

@router.post('/forgot-password')
def forgot_password(req: ForgotPasswordRequestSchema, db: Session = Depends(get_db)):
    service = AuthService(db)
    token = service.forgot_password(req.email)
    return {"success": True, "message": "Password reset token generated.", "reset_token": token}

@router.post('/reset-password')
def reset_password(req: ResetPasswordRequestSchema, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.reset_password(req.token, req.new_password)
    return {"success": True, "message": "Password reset successfully."}

@router.get('/me')
def get_me(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    player_repo = PlayerRepository(db)
    profile = player_repo.get_profile(user.id)
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_guest": user.is_guest,
        "display_name": profile.display_name if profile else user.username,
        "country": profile.country if profile else "Global",
        "theme": profile.theme if profile else "default",
        "created_at": user.created_at
    }

@router.get('/sessions')
def get_sessions(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    service = AuthService(db)
    sessions = service.auth_repo.get_user_sessions(user.id)
    return [
        {
            "id": s.id,
            "ip_address": s.ip_address,
            "user_agent": s.user_agent,
            "success": s.success
        } for s in sessions
    ]

@router.delete('/sessions/{session_id}')
def delete_session(session_id: int, user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    return {"success": True, "message": f"Session {session_id} revoked."}
