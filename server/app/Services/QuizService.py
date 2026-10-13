import os
import requests
from app.Database.UserRepository import UserRepository


class QuizService:
    """
    The main server does not work with quizzes itself - it forwards every request
    to the Quiz Service (HTTP) and adds who the logged-in user is.
    The client never talks to the Quiz Service directly.
    """

    def __init__(self):
        self.base_url = os.getenv("QUIZ_SERVICE_URL", "http://localhost:5001") + "/quizzes"
        self.internal_key = os.getenv("INTERNAL_API_KEY", "")
        self.user_repo = UserRepository()

    def create_quiz(self, user_id: int, data):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"error": "User not found"}, 404
        body = self._with_author(data, user)
        return self._send("POST", "", user, body)

    def update_quiz(self, user_id: int, quiz_id: str, data):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"error": "User not found"}, 404
        body = self._with_author(data, user)
        return self._send("PUT", f"/{quiz_id}", user, body)

    def delete_quiz(self, user_id: int, quiz_id: str):
        return self._send_as(user_id, "DELETE", f"/{quiz_id}")

    def get_all_quizzes(self, user_id: int):
        return self._send_as(user_id, "GET", "")

    def get_my_quizzes(self, user_id: int):
        return self._send_as(user_id, "GET", "/mine")

    def get_published_quizzes(self, user_id: int):
        return self._send_as(user_id, "GET", "/published")

    def get_quiz(self, user_id: int, quiz_id: str):
        return self._send_as(user_id, "GET", f"/{quiz_id}")

    def review_quiz(self, user_id: int, quiz_id: str, data):
        return self._send_as(user_id, "PATCH", f"/{quiz_id}/review", data)

    def submit_answers(self, user_id: int, quiz_id: str, data):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"error": "User not found"}, 404

        body = dict(data) if isinstance(data, dict) else {}
        body["user_name"] = user.get_full_name()
        body["user_email"] = user.email
        return self._send("POST", f"/{quiz_id}/submit", user, body)

    def get_leaderboard(self, user_id: int, quiz_id: str):
        return self._send_as(user_id, "GET", f"/{quiz_id}/leaderboard")

    # HELPERS

    @staticmethod
    def _with_author(data, user):
        """The author is always the logged-in user - never what the client sends."""
        body = dict(data) if isinstance(data, dict) else {}
        body.pop("author_id", None)
        body["author_name"] = user.get_full_name()
        body["author_email"] = user.email
        return body

    def _send_as(self, user_id: int, method: str, path: str, body=None):
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return {"error": "User not found"}, 404
        return self._send(method, path, user, body)

    def _send(self, method: str, path: str, user, body=None):
        headers = {
            "X-Internal-Key": self.internal_key,
            "X-User-Id": str(user.id),
            "X-User-Role": user.role.value,
        }

        try:
            response = requests.request(method, self.base_url + path, json=body, headers=headers, timeout=5)
        except requests.RequestException:
            return {"error": "Quiz service is not available"}, 503

        try:
            return response.json(), response.status_code
        except ValueError:
            return {"error": "Invalid response from quiz service"}, 502
