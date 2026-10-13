from enum import Enum


class QuizStatus(str, Enum):
    PENDING = "PENDING"      # waiting for the admin
    APPROVED = "APPROVED"    # visible to players
    REJECTED = "REJECTED"    # returned to the moderator with a reason
