from datetime import datetime
from src.infrastructure.database.session import db

class UserModel(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(50), default='user')
    provider = db.Column(db.String(50), default='local')
    provider_id = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_entity(self):
        from src.domain.entities.user import User, UserRole, AuthProvider
        return User(
            id=self.id,
            email=self.email,
            username=self.username,
            password_hash=self.password_hash,
            role=UserRole(self.role),
            provider=AuthProvider(self.provider),
            provider_id=self.provider_id,
            is_active=self.is_active,
            is_verified=self.is_verified,
            last_login=self.last_login,
            created_at=self.created_at,
            updated_at=self.updated_at
        )
    
    @classmethod
    def from_entity(cls, user_entity):
        return cls(
            email=user_entity.email,
            username=user_entity.username,
            password_hash=user_entity.password_hash,
            role=user_entity.role.value,
            provider=user_entity.provider.value,
            provider_id=user_entity.provider_id,
            is_active=user_entity.is_active,
            is_verified=user_entity.is_verified,
            last_login=user_entity.last_login
        )