from typing import Optional
from datetime import datetime
from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ..database.models import UserModel
from ..database.session import db

class UserRepositoryImpl(UserRepository):
    
    def find_by_email(self, email: str) -> Optional[User]:
        user_model = UserModel.query.filter_by(email=email).first()
        return user_model.to_entity() if user_model else None
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        user_model = UserModel.query.get(user_id)
        return user_model.to_entity() if user_model else None
    
    def find_by_provider(self, provider: str, provider_id: str) -> Optional[User]:
        user_model = UserModel.query.filter_by(
            provider=provider, 
            provider_id=provider_id
        ).first()
        return user_model.to_entity() if user_model else None
    
    def save(self, user: User) -> User:
        user_model = UserModel.from_entity(user)
        db.session.add(user_model)
        db.session.commit()
        return user_model.to_entity()
    
    def update(self, user: User) -> User:
        user_model = UserModel.query.get(user.id)
        if user_model:
            user_model.email = user.email
            user_model.username = user.username
            user_model.password_hash = user.password_hash
            user_model.role = user.role.value
            user_model.provider = user.provider.value
            user_model.provider_id = user.provider_id
            user_model.is_active = user.is_active
            user_model.is_verified = user.is_verified
            user_model.last_login = user.last_login
            db.session.commit()
            return user_model.to_entity()
        return user
    
    def delete(self, user_id: int) -> bool:
        user_model = UserModel.query.get(user_id)
        if user_model:
            db.session.delete(user_model)
            db.session.commit()
            return True
        return False
    
    def update_last_login(self, user_id: int) -> None:
        user_model = UserModel.query.get(user_id)
        if user_model:
            user_model.last_login = datetime.utcnow()
            db.session.commit()