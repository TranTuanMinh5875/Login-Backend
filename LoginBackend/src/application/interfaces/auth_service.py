from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class AuthService(ABC):
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        pass
    
    @abstractmethod
    def verify_password(self, password: str, hashed_password: str) -> bool:
        pass
    
    @abstractmethod
    def create_access_token(
        self, 
        user_id: int, 
        role: str, 
        expires_minutes: int = 1440,
        is_guest: bool = False
    ) -> str:
        pass
    
    @abstractmethod
    def create_refresh_token(self, user_id: int) -> str:
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        pass