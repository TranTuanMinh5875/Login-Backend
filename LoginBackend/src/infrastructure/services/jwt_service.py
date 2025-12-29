import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from ...application.interfaces.auth_service import AuthService
from ...infrastructure.config.settings import settings
from src.infrastructure.services.bcrypt_service import BcryptService

class JWTService(AuthService):
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
    
    def hash_password(self, password: str) -> str:
        return BcryptService.hash_password(password)
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        return BcryptService.verify_password(password, hashed_password)
    
    def create_access_token(
        self, 
        user_id: int, 
        role: str, 
        expires_minutes: int = 1440,
        is_guest: bool = False
    ) -> str:
        expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
        payload = {
            'sub': str(user_id),
            'role': role,
            'is_guest': is_guest,
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: int) -> str:
        expire = datetime.utcnow() + timedelta(days=30)
        payload = {
            'sub': str(user_id),
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except:
            return None