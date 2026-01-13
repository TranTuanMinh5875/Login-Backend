from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"
    RESTAURANT_STAFF = "restaurant_staff"
    GUEST = "guest"

class AuthProvider(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"

@dataclass
class User:
    id: Optional[int] = None
    email: str = ""
    username: Optional[str] = None
    password_hash: Optional[str] = None
    role: UserRole = UserRole.USER
    provider: AuthProvider = AuthProvider.LOCAL
    provider_id: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def is_guest(self) -> bool:
        return self.role == UserRole.GUEST
    
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    
    def is_restaurant_staff(self) -> bool:
        return self.role == UserRole.RESTAURANT_STAFF
    
    def is_regular_user(self) -> bool:
        return self.role == UserRole.USER