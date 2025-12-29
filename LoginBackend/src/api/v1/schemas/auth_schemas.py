from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    RESTAURANT_STAFF = "restaurant_staff"
    GUEST = "guest"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False
    role: UserRole = UserRole.USER

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: Optional[str] = None
    role: UserRole = UserRole.USER
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v

class QuickLoginRequest(BaseModel):
    role: UserRole

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int
    user: dict

class UserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str]
    role: str
    is_active: bool
    created_at: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None