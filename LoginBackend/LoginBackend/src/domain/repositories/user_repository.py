from abc import ABC, abstractmethod
from typing import Optional
from ..entities.user import User

class UserRepository(ABC):
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_by_provider(self, provider: str, provider_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> User:
        pass
    
    @abstractmethod
    def update(self, user: User) -> User:
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass
    
    @abstractmethod
    def update_last_login(self, user_id: int) -> None:
        pass