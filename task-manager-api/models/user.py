from database import db
from utils.timeutils import now_utc
import hashlib


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=now_utc)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def public_dict(self):
        """User fields safe for list responses (excludes the password hash)."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, raw_password):
        self.password = hashlib.md5(raw_password.encode()).hexdigest()

    def check_password(self, raw_password):
        return self.password == hashlib.md5(raw_password.encode()).hexdigest()

    def is_admin(self):
        return self.role == 'admin'
