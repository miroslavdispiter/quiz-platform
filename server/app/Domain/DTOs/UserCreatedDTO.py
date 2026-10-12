from dataclasses import dataclass
from app.Domain.enums.role import Role

@dataclass
class UserCreatedDTO:
    id: int
    email: str
    role: Role
    created_at: str

    # MAP
    @staticmethod
    def from_model(user) -> "UserCreatedDTO":
        return UserCreatedDTO(
            id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )