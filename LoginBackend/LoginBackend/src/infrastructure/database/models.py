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
    
class OrderModel(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(100))
    table_number = db.Column(db.String(20))
    items = db.Column(db.Text)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    kitchen_notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    creator = db.relationship('UserModel', foreign_keys=[created_by])
    assignee = db.relationship('UserModel', foreign_keys=[assigned_to])
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_number': self.order_number,
            'customer_name': self.customer_name,
            'table_number': self.table_number,
            'items': self.items,
            'total_amount': self.total_amount,
            'status': self.status,
            'kitchen_notes': self.kitchen_notes,
            'created_by': self.created_by,
            'assigned_to': self.assigned_to,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }