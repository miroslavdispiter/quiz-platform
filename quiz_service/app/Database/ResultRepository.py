from datetime import datetime, timezone
from bson import ObjectId
from app.Database.db import results_collection
from app.Domain.enums.result_status import ResultStatus


class ResultRepository:
    """All work with the "results" collection in MongoDB."""

    def create(self, result: dict) -> str:
        inserted = results_collection.insert_one(result)
        return str(inserted.inserted_id)

    def get_by_id(self, result_id: str):
        if not ObjectId.is_valid(result_id):
            return None
        return results_collection.find_one({"_id": ObjectId(result_id)})

    def mark_done(self, result_id: str, score: int, correct_count: int) -> None:
        results_collection.update_one(
            {"_id": ObjectId(result_id)},
            {"$set": {
                "score": score,
                "correct_count": correct_count,
                "status": ResultStatus.DONE.value,
                "finished_at": datetime.now(timezone.utc),
            }},
        )

    def get_leaderboard(self, quiz_id: str) -> list:
        # Only processed results: more points first, then less time spent
        return list(
            results_collection
            .find({"quiz_id": quiz_id, "status": ResultStatus.DONE.value})
            .sort([("score", -1), ("time_spent", 1)])
        )

    def delete_by_quiz(self, quiz_id: str) -> None:
        results_collection.delete_many({"quiz_id": quiz_id})
