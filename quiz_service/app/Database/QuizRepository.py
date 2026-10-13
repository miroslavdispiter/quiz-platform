from bson import ObjectId
from app.Database.db import quizzes_collection


class QuizRepository:
    """All work with the "quizzes" collection in MongoDB."""

    def create(self, quiz: dict) -> str:
        result = quizzes_collection.insert_one(quiz)
        return str(result.inserted_id)

    def get_by_id(self, quiz_id: str):
        if not ObjectId.is_valid(quiz_id):
            return None
        return quizzes_collection.find_one({"_id": ObjectId(quiz_id)})

    def get_all(self) -> list:
        return list(quizzes_collection.find().sort("created_at", -1))

    def get_by_status(self, status: str) -> list:
        return list(quizzes_collection.find({"status": status}).sort("created_at", -1))

    def get_by_author(self, author_id: int) -> list:
        return list(quizzes_collection.find({"author_id": author_id}).sort("created_at", -1))

    def update(self, quiz_id: str, fields: dict) -> None:
        quizzes_collection.update_one({"_id": ObjectId(quiz_id)}, {"$set": fields})

    def delete(self, quiz_id: str) -> bool:
        if not ObjectId.is_valid(quiz_id):
            return False
        result = quizzes_collection.delete_one({"_id": ObjectId(quiz_id)})
        return result.deleted_count == 1
