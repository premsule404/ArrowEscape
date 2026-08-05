from fastapi import APIRouter, HTTPException, Depends
from ..schemas.user import UserCreate, UserLogin, Token, UserResponse
from ..core.security import create_access_token, get_password_hash, verify_password
from datetime import timedelta
from ..core.config import settings

router = APIRouter()

# Mock DB for Phase 6 (Replaced in Phase 7)
MOCK_USERS = {}
user_counter = 1

@router.post("/signup", response_model=Token)
def signup(user_in: UserCreate):
    global user_counter
    if user_in.username in MOCK_USERS:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_pwd = get_password_hash(user_in.password) if user_in.password else ""
    
    MOCK_USERS[user_in.username] = {
        "id": user_counter,
        "username": user_in.username,
        "hashed_password": hashed_pwd,
        "is_guest": user_in.is_guest
    }
    user_counter += 1
    
    access_token = create_access_token(
        data={"sub": user_in.username}, 
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user_in: UserLogin):
    user = MOCK_USERS.get(user_in.username)
    if not user or not verify_password(user_in.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
        
    access_token = create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/guest", response_model=Token)
def guest_login():
    global user_counter
    guest_username = f"Guest_{user_counter}"
    
    MOCK_USERS[guest_username] = {
        "id": user_counter,
        "username": guest_username,
        "hashed_password": "",
        "is_guest": True
    }
    user_counter += 1
    
    access_token = create_access_token(
        data={"sub": guest_username}, 
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
