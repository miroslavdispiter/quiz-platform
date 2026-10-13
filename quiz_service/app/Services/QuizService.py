from dataclasses import asdict
from datetime import datetime, timezone
from app.Database.QuizRepository import QuizRepository
from app.Database.ResultRepository import ResultRepository
from app.Domain.DTOs.QuizDTO import QuizDTO
from app.Domain.DTOs.QuizSummaryDTO import QuizSummaryDTO
from app.Domain.enums.quiz_status import QuizStatus
from app.Domain.enums.role import Role


class QuizService:
    """Creating, editing, deleting, reviewing and reading quizzes."""

    def __init__(self):
        self.quiz_repo = QuizRepository()
        self.result_repo = ResultRepository()

    # CREATE QUIZ (moderator)
    def create_quiz(self, data, user):
        quiz = {
            "title": data["title"].strip(),
            "duration": data["duration"],
            "author_id": user["id"],
            "author_name": data["author_name"],
            "author_email": data.get("author_email"),
            "status": QuizStatus.PENDING.value,
            "rejection_reason": None,
            "questions": self._clean_questions(data["questions"]),
            "created_at": datetime.now(timezone.utc),
        }

        quiz["_id"] = self.quiz_repo.create(quiz)
        return asdict(QuizDTO.from_document(quiz)), 201

    # EDIT QUIZ (only the author) - the quiz goes back to the admin for approval
    def update_quiz(self, quiz_id, data, user):
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if not quiz:
            return {"error": "Quiz not found"}, 404

        if quiz["author_id"] != user["id"]:
            return {"error": "You can edit only your own quizzes"}, 403

        self.quiz_repo.update(quiz_id, {
            "title": data["title"].strip(),
            "duration": data["duration"],
            "questions": self._clean_questions(data["questions"]),
            "status": QuizStatus.PENDING.value,
            "rejection_reason": None,
        })

        updated = self.quiz_repo.get_by_id(quiz_id)
        return asdict(QuizDTO.from_document(updated)), 200

    # DELETE QUIZ (author moderator or admin)
    def delete_quiz(self, quiz_id, user):
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if not quiz:
            return {"error": "Quiz not found"}, 404

        if user["role"] == Role.MODERATOR.value and quiz["author_id"] != user["id"]:
            return {"error": "You can delete only your own quizzes"}, 403

        self.quiz_repo.delete(quiz_id)
        self.result_repo.delete_by_quiz(quiz_id)
        return {"_id": quiz_id, "title": quiz["title"], "message": "Quiz deleted"}, 200

    # ALL QUIZZES (admin)
    def get_all_quizzes(self):
        quizzes = self.quiz_repo.get_all()
        return [asdict(QuizSummaryDTO.from_document(q)) for q in quizzes], 200

    # MY QUIZZES (moderator)
    def get_my_quizzes(self, user):
        quizzes = self.quiz_repo.get_by_author(user["id"])
        return [asdict(QuizSummaryDTO.from_document(q)) for q in quizzes], 200

    # APPROVED QUIZZES (players)
    def get_published_quizzes(self):
        quizzes = self.quiz_repo.get_by_status(QuizStatus.APPROVED.value)
        return [asdict(QuizSummaryDTO.from_document(q)) for q in quizzes], 200

    # ONE QUIZ - what is shown depends on the role
    def get_quiz(self, quiz_id, user):
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if not quiz:
            return {"error": "Quiz not found"}, 404

        role = user["role"]

        # Player sees only approved quizzes and never the correct answers
        if role == Role.PLAYER.value:
            if quiz["status"] != QuizStatus.APPROVED.value:
                return {"error": "Quiz not found"}, 404
            return asdict(QuizDTO.from_document(quiz, hide_answers=True)), 200

        # Moderator sees only his own quizzes
        if role == Role.MODERATOR.value and quiz["author_id"] != user["id"]:
            return {"error": "You can view only your own quizzes"}, 403

        return asdict(QuizDTO.from_document(quiz)), 200

    # APPROVE / REJECT (admin)
    def review_quiz(self, quiz_id, data):
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if not quiz:
            return {"error": "Quiz not found"}, 404

        if quiz["status"] != QuizStatus.PENDING.value:
            return {"error": "Only quizzes waiting for approval can be reviewed"}, 409

        status = data["status"]
        reason = data["rejection_reason"].strip() if status == QuizStatus.REJECTED.value else None

        self.quiz_repo.update(quiz_id, {"status": status, "rejection_reason": reason})

        updated = self.quiz_repo.get_by_id(quiz_id)
        return asdict(QuizDTO.from_document(updated)), 200

    @staticmethod
    def _clean_questions(questions):
        """Keeps only the fields we need and removes extra spaces."""
        return [
            {
                "text": q["text"].strip(),
                "options": [o.strip() for o in q["options"]],
                "correct_answers": [a.strip() for a in q["correct_answers"]],
                "points": q["points"],
            }
            for q in questions
        ]
