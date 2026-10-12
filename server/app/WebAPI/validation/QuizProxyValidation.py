import re
from flask import jsonify
from typing import Optional, Tuple


class QuizProxyValidation:
    """
    Validacija podataka za Quiz Proxy Controller - serverska strana (main server).
    """

    OBJECT_ID_REGEX = r'^[a-fA-F0-9]{24}$'
    EMAIL_REGEX = r"^[\w\.+-]+@[\w\.-]+\.\w+$"  # dozvoljen i "+" (npr. ime+igrac@gmail.com)
    VALID_STATUSES = ["APPROVED", "REJECTED"]

    MIN_REJECTION_REASON_LENGTH = 5
    MAX_REJECTION_REASON_LENGTH = 500

    @staticmethod
    def validate_quiz_id(quiz_id: str) -> Optional[Tuple]:
        """
        Validacija MongoDB ObjectId formata.
        """
        if not quiz_id:
            return jsonify({"error": "Quiz ID is required"}), 400

        if not re.match(QuizProxyValidation.OBJECT_ID_REGEX, str(quiz_id)):
            return jsonify({"error": "Invalid quiz ID format"}), 400

        return None 

    @staticmethod
    def validate_review_data(data: dict) -> Optional[Tuple]:
        """
        Validacija podataka za review (approve/reject) kviza.
        """
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        # Status
        status = data.get("status")
        if not status:
            return jsonify({"error": "Status is required"}), 400

        status = str(status).upper()
        if status not in QuizProxyValidation.VALID_STATUSES:
            return jsonify({
                "error": f"Status must be one of: {', '.join(QuizProxyValidation.VALID_STATUSES)}"
            }), 400

        if status == "REJECTED":
            reason = data.get("rejection_reason", "")
            if not reason or not str(reason).strip():
                return jsonify({
                    "error": "Rejection reason is required when rejecting a quiz"
                }), 400

            reason = str(reason).strip()
            if len(reason) < QuizProxyValidation.MIN_REJECTION_REASON_LENGTH:
                return jsonify({
                    "error": f"Rejection reason must be at least {QuizProxyValidation.MIN_REJECTION_REASON_LENGTH} characters"
                }), 400

            if len(reason) > QuizProxyValidation.MAX_REJECTION_REASON_LENGTH:
                return jsonify({
                    "error": f"Rejection reason must not exceed {QuizProxyValidation.MAX_REJECTION_REASON_LENGTH} characters"
                }), 400

        return None

    @staticmethod
    def validate_submit_data(data: dict) -> Optional[Tuple]:
        """
        Validacija podataka za slanje odgovora na kviz.
        """
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        answers = data.get("answers")
        if answers is None:
            return jsonify({"error": "Answers are required"}), 400

        if not isinstance(answers, list):
            return jsonify({"error": "Answers must be an array"}), 400

        seen_indices = set()
        for idx, answer in enumerate(answers):
            if not isinstance(answer, dict):
                return jsonify({
                    "error": f"Answer {idx + 1}: Invalid format, must be an object"
                }), 400

            question_index = answer.get("question_index")
            if question_index is None:
                return jsonify({
                    "error": f"Answer {idx + 1}: question_index is required"
                }), 400

            try:
                question_index = int(question_index)
                if question_index < 0:
                    return jsonify({
                        "error": f"Answer {idx + 1}: question_index cannot be negative"
                    }), 400
            except (ValueError, TypeError):
                return jsonify({
                    "error": f"Answer {idx + 1}: question_index must be a valid number"
                }), 400

            if question_index in seen_indices:
                return jsonify({
                    "error": f"Answer {idx + 1}: Duplicate answer for question {question_index + 1}"
                }), 400
            seen_indices.add(question_index)

            selected = answer.get("selected")
            if selected is not None and not isinstance(selected, list):
                return jsonify({
                    "error": f"Answer {idx + 1}: 'selected' must be an array"
                }), 400

        time_spent = data.get("time_spent")
        if time_spent is not None:
            try:
                time_spent = int(time_spent)
                if time_spent < 0:
                    return jsonify({"error": "time_spent cannot be negative"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "time_spent must be a valid number"}), 400

        return None  

    @staticmethod
    def validate_delete_request(data: dict) -> Optional[Tuple]:
        """
        Validacija podataka za brisanje kviza (opciono, ako ima payload).
        """
        if data:
            requester_role = data.get("requester_role")
            requester_id = data.get("requester_id")

            if requester_role and requester_role not in ["ADMIN", "MODERATOR", "PLAYER"]:
                return jsonify({"error": "Invalid requester_role"}), 400

        return None

    @staticmethod
    def validate_internal_result(data: dict) -> Optional[Tuple]:
        """
        Validacija podataka za interno čuvanje rezultata kviza.
        """
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        required_fields = ["user_email", "quiz_id", "quiz_title", "score", "total_questions", "percentage"]
        missing = [f for f in required_fields if data.get(f) is None]

        if missing:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing)}"
            }), 400

        user_email = data.get("user_email")
        if not re.match(QuizProxyValidation.EMAIL_REGEX, str(user_email)):
            return jsonify({"error": "Invalid user_email format"}), 400

        quiz_id = data.get("quiz_id")
        if not re.match(QuizProxyValidation.OBJECT_ID_REGEX, str(quiz_id)):
            return jsonify({"error": "Invalid quiz_id format"}), 400

        try:
            score = int(data.get("score"))
            if score < 0:
                return jsonify({"error": "Score cannot be negative"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Score must be a valid number"}), 400

        try:
            total_questions = int(data.get("total_questions"))
            if total_questions <= 0:
                return jsonify({"error": "total_questions must be positive"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "total_questions must be a valid number"}), 400

        try:
            percentage = float(data.get("percentage"))
            if percentage < 0 or percentage > 100:
                return jsonify({"error": "Percentage must be between 0 and 100"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Percentage must be a valid number"}), 400

        time_spent = data.get("time_spent")
        if time_spent is not None:
            try:
                time_spent = int(time_spent)
                if time_spent < 0:
                    return jsonify({"error": "time_spent cannot be negative"}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "time_spent must be a valid number"}), 400

        return None

    @staticmethod
    def validate_notify_admin(data: dict) -> Optional[Tuple]:
        """
        Validacija podataka za notifikaciju admina o novom kvizu.
        """
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        quiz_id = data.get("quiz_id")
        title = data.get("title")

        if not quiz_id:
            return jsonify({"error": "quiz_id is required"}), 400

        if not re.match(QuizProxyValidation.OBJECT_ID_REGEX, str(quiz_id)):
            return jsonify({"error": "Invalid quiz_id format"}), 400

        if not title or not str(title).strip():
            return jsonify({"error": "Quiz title is required"}), 400

        return None  # Validno