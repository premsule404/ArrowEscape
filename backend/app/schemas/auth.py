from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class RegisterRequestSchema(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    display_name: Optional[str] = None

class LoginRequestSchema(BaseModel):
    username: str
    password: str

class GuestLoginRequestSchema(BaseModel):
    display_name: Optional[str] = None

class GuestUpgradeRequestSchema(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class TokenResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    is_guest: bool

class RefreshTokenRequestSchema(BaseModel):
    refresh_token: str

class EmailVerificationRequestSchema(BaseModel):
    token: str

class ForgotPasswordRequestSchema(BaseModel):
    email: str

class ResetPasswordRequestSchema(BaseModel):
    token: str
    new_password: str

class SessionItemSchema(BaseModel):
    id: int
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None
    is_current: bool = False
