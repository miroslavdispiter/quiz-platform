from dataclasses import dataclass
from app.Domain.enums.role import Role

@dataclass
class UserSummaryDTO:
    id: int
    full_name: str
    email: str
    role: Role
    country: str
    created_at: str

    # MAP
    @staticmethod
    def from_model(user) -> "UserSummaryDTO":
        return UserSummaryDTO(
            id=user.id,
            full_name=f"{user.first_name} {user.last_name}",
            email=user.email,
            role=user.role,
            country=user.country,
            created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )