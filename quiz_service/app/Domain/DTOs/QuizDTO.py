from dataclasses import dataclass
from typing import List, Optional


@dataclass
class QuestionDTO:
    text: str
    options: List[str]
    points: int
    correct_answers: List[str]


@dataclass
class PlayerQuestionDTO:
    """Question as the player sees it - WITHOUT the correct answers."""
    text: str
    options: List[str]
    points: int


@dataclass
class QuizDTO:
    _id: str
    title: str
    duration: int  # seconds
    author_id: int
    author_name: str
    status: str
    rejection_reason: Optional[str]
    created_at: str
    questions: list

    # MAP
    @staticmethod
    def from_document(doc, hide_answers: bool = False) -> "QuizDTO":
        if hide_answers:
            questions = [
                PlayerQuestionDTO(text=q["text"], options=q["options"], points=q["points"])
                for q in doc["questions"]
            ]
        else:
            questions = [
                QuestionDTO(
                    text=q["text"],
                    options=q["options"],
                    points=q["points"],
                    correct_answers=q["correct_answers"],
                )
                for q in doc["questions"]
            ]

        return QuizDTO(
            _id=str(doc["_id"]),
            title=doc["title"],
            duration=doc["duration"],
            author_id=doc["author_id"],
            author_name=doc["author_name"],
            status=doc["status"],
            rejection_reason=doc.get("rejection_reason"),
            created_at=doc["created_at"].isoformat(),
            questions=questions,
        )
