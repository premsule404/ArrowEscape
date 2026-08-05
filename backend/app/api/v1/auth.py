import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from ...db.session import get_db
from ...models.user import User, PlayerProfile, UserProgressSummary, Settings, RefreshToken
from ...schemas.user import UserCreate, UserLogin, GuestLogin, Token, UserProfileResponse
from ...core.security import verify_password, get_password_hash, create_access_token
from ...core.config import settings

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            return None
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        return None
        
    user = db.query(User).filter(User.id == user_id, User.account_status == "active").first()
    return user

def require_current_user(user: Optional[User] = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post('/register', response_model=Token)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(
        (User.username == user_in.username) | 
        (User.email == user_in.email if user_in.email else False)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username or Email already registered")
        
    pwd_hash = get_password_hash(user_in.password) if user_in.password else None
    
    new_user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=pwd_hash,
        is_guest=user_in.is_guest
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Initialize profile and summary
    profile = PlayerProfile(user_id=new_user.id, display_name=new_user.username)
    summary = UserProgressSummary(user_id=new_user.id)
    user_settings = Settings(user_id=new_user.id)
    db.add(profile)
    db.add(summary)
    db.add(user_settings)
    db.commit()
    
    access_token = create_access_token({"sub": str(new_user.id)})
    refresh_token_str = str(uuid.uuid4())
    
    rf = RefreshToken(
        user_id=new_user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(rf)
    db.commit()
    
    return {"access_token": access_token, "refresh_token": refresh_token_str, "token_type": "bearer"}

@router.post('/login', response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == user_in.username) | (User.email == user_in.username)
    ).first()
    
    if not user or not user.password_hash or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")
        
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token_str = str(uuid.uuid4())
    
    rf = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(rf)
    db.commit()
    
    return {"access_token": access_token, "refresh_token": refresh_token_str, "token_type": "bearer"}

@router.post('/guest', response_model=Token)
def guest_login(guest_in: GuestLogin, db: Session = Depends(get_db)):
    guest_username = f"Guest_{uuid.uuid4().hex[:8]}"
    new_user = User(username=guest_username, is_guest=True)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    display = guest_in.display_name or f"Guest #{new_user.id}"
    profile = PlayerProfile(user_id=new_user.id, display_name=display)
    summary = UserProgressSummary(user_id=new_user.id)
    user_settings = Settings(user_id=new_user.id)
    db.add(profile)
    db.add(summary)
    db.add(user_settings)
    db.commit()
    
    access_token = create_access_token({"sub": str(new_user.id)})
    refresh_token_str = str(uuid.uuid4())
    
    rf = RefreshToken(
        user_id=new_user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    db.add(rf)
    db.commit()
    
    return {"access_token": access_token, "refresh_token": refresh_token_str, "token_type": "bearer"}

@router.get('/me', response_model=UserProfileResponse)
def get_me(user: User = Depends(require_current_user), db: Session = Depends(get_db)):
    profile = db.query(PlayerProfile).filter(PlayerProfile.user_id == user.id).first()
    summary = db.query(UserProgressSummary).filter(UserProgressSummary.user_id == user.id).first()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "display_name": profile.display_name if profile else user.username,
        "avatar": profile.avatar if profile else None,
        "country": profile.country if profile else "Global",
        "preferred_language": profile.preferred_language if profile else "en",
        "theme": profile.theme if profile else "default",
        "is_guest": user.is_guest,
        "is_admin": user.is_admin,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "total_coins": summary.total_coins if summary else 0,
        "total_stars": summary.total_stars if summary else 0,
        "completed_levels": summary.completed_levels if summary else 0,
        "current_level": summary.current_level if summary else 1
    }
