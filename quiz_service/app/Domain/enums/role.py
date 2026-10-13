from enum import Enum


class Role(str, Enum):
    PLAYER = "PLAYER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"
