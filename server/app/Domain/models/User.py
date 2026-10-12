from app.Database.db import db
from app.Domain.enums.role import Role
from datetime import datetime
from app.Extensions.bcrypt import bcrypt

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)

    country = db.Column(db.String(60), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    street_number = db.Column(db.String(20), nullable=False)

    role = db.Column(db.Enum(Role), default=Role.PLAYER, nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)

    failed_attempts = db.Column(db.Integer, default=0, nullable=False)
    blocked_until = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    
    def verify_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def is_blocked(self) -> bool:
        if self.blocked_until is None:
            return False
        return self.blocked_until > datetime.utcnow()

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def get_full_address(self) -> str:
        return f"{self.street} {self.street_number}, {self.country}"

    def __repr__(self):
        return f"<User {self.email}>"