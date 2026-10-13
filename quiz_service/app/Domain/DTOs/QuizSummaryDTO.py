from dataclasses import dataclass
from typing import Optional


@dataclass
class QuizSummaryDTO:
    """Quiz shown in lists (without questions)."""
    _id: str
    title: str
    duration: int  # seconds
    author_id: int
    author_name: str
    status: str
    rejection_reason: Optional[str]
    question_count: int
    created_at: str

    # MAP
    @staticmethod
    def from_document(doc) -> "QuizSummaryDTO":
        return QuizSummaryDTO(
            _id=str(doc["_id"]),
            title=doc["title"],
            duration=doc["duration"],
            author_id=doc["author_id"],
            author_name=doc["author_name"],
            status=doc["status"],
            rejection_reason=doc.get("rejection_reason"),
            question_count=len(doc["questions"]),
            created_at=doc["created_at"].isoformat(),
        )
