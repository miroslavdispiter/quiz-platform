from dataclasses import dataclass


@dataclass
class LeaderboardEntryDTO:
    user_id: int
    full_name: str
    score: int
    max_score: int
    time_spent: int  # seconds

    # MAP
    @staticmethod
    def from_document(doc) -> "LeaderboardEntryDTO":
        return LeaderboardEntryDTO(
            user_id=doc["user_id"],
            full_name=doc["user_name"],
            score=doc["score"],
            max_score=doc["max_score"],
            time_spent=doc["time_spent"],
        )
