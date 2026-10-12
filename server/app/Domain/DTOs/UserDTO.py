from dataclasses import dataclass
from typing import Optional
from app.Domain.enums.role import Role

@dataclass
class UserDTO:
    id: int
    first_name: str
    last_name: str
    email: str
    date_of_birth: Optional[str]  # "YYYY-MM-DD"
    gender: str
    country: str
    street: str
    street_number: str
    role: Role
    profile_image: Optional[str]
    created_at: str
    updated_at: Optional[str]

    # MAP
    @staticmethod
    def from_model(user) -> "UserDTO":
        return UserDTO(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            date_of_birth=user.date_of_birth.isoformat() if user.date_of_birth else None,
            gender=user.gender,
            country=user.country,
            street=user.street,
            street_number=user.street_number,
            role=user.role,
            profile_image=user.profile_image,
            created_at=user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=user.updated_at.strftime("%Y-%m-%d %H:%M:%S") if user.updated_at else None
        )