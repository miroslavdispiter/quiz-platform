from enum import Enum


class Role(str, Enum):
    """User roles, same values as in the main server (JWT "role" claim)."""

    PLAYER = "PLAYER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"
