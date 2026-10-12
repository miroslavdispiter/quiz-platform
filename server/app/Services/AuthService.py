from flask_jwt_extended import create_access_token
from app.Domain.models.User import User
from datetime import datetime, timedelta
from app.Database.db import db

class AuthResult:
    SUCCESS = "SUCCESS"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    BLOCKED = "BLOCKED"

class AuthService:
    def login(self, user: User | None, password: str):
        
        # User doesn't exist
        if user is None:
            return AuthResult.INVALID_CREDENTIALS, None
        
        # User is blocked
        if user.blocked_until and user.blocked_until > datetime.utcnow():
            return AuthResult.BLOCKED, None
        
        # Wrong password
        if not user.verify_password(password):
            user.failed_attempts += 1

            if user.failed_attempts >= 3:
                user.blocked_until = datetime.utcnow() + timedelta(minutes=1)
                user.failed_attempts = 0
        
            db.session.commit()
            return AuthResult.INVALID_CREDENTIALS, None
        
        user.failed_attempts = 0
        user.blocked_until = None
        db.session.commit()

        print(">>> user.id =", user.id, type(user.id))
        print(">>> user.role =", user.role)

        token = create_access_token(
            identity=str(user.id),
            additional_claims={"role": user.role.value}
        )

        return AuthResult.SUCCESS, token