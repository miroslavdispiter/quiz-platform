import multiprocessing
from dataclasses import asdict
from datetime import datetime, timezone
from app.Database.QuizRepository import QuizRepository
from app.Database.ResultRepository import ResultRepository
from app.Domain.DTOs.LeaderboardEntryDTO import LeaderboardEntryDTO
from app.Domain.DTOs.SubmitResponseDTO import SubmitResponseDTO
from app.Domain.enums.quiz_status import QuizStatus
from app.Domain.enums.result_status import ResultStatus
from app.Services.quiz_processing import process_result
from app.Extensions.cache import cache, leaderboard_key


class ResultService:
    """Submitting answers (asynchronous processing) and the leaderboard."""

    def __init__(self):
        self.quiz_repo = QuizRepository()
        self.result_repo = ResultRepository()

    # PLAYER SUBMITS ANSWERS
    def submit_answers(self, quiz_id, data, user):
        quiz = self.quiz_repo.get_by_id(quiz_id)
        if not quiz or quiz["status"] != QuizStatus.APPROVED.value:
            return {"error": "Quiz not found"}, 404

        # Time spent can never be longer than the quiz lasts
        time_spent = min(data["time_spent"], quiz["duration"])

        result = {
            "quiz_id": quiz_id,
            "quiz_title": quiz["title"],
            "user_id": user["id"],
            "user_name": data["user_name"],
            "user_email": data.get("user_email"),
            "answers": data["answers"],
            "time_spent": time_spent,
            "score": None,
            "max_score": sum(q["points"] for q in quiz["questions"]),
            "correct_count": None,
            "status": ResultStatus.PROCESSING.value,
            "created_at": datetime.now(timezone.utc),
            "finished_at": None,
        }
        result_id = self.result_repo.create(result)

        # PROCESS: the answers are processed in a separate process,
        # so this request returns immediately and the player can continue using the platform.
        process = multiprocessing.get_context("spawn").Process(target=process_result, args=(result_id,))
        process.start()

        response = SubmitResponseDTO(
            result_id=result_id,
            status=ResultStatus.PROCESSING.value,
            message="Your answers are being processed. The result will be sent to your email.",
        )
        return asdict(response), 202

    # LEADERBOARD FOR ONE QUIZ - read from the cache when possible
    def get_leaderboard(self, quiz_id):
        cached = cache.get(leaderboard_key(quiz_id))
        if cached is not None:
            return cached, 200

        quiz = self.quiz_repo.get_by_id(quiz_id)
        if not quiz:
            return {"error": "Quiz not found"}, 404

        results = self.result_repo.get_leaderboard(quiz_id)
        leaderboard = [asdict(LeaderboardEntryDTO.from_document(r)) for r in results]

        cache.set(leaderboard_key(quiz_id), leaderboard)
        return leaderboard, 200
