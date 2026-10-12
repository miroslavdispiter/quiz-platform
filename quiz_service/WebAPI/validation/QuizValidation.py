# quiz_service/WebAPI/validation/QuizValidation.py

import re
from flask import jsonify
from typing import Optional, Tuple

class QuizValidation:
    """
    Validacija podataka za kvizove - serverska strana.
    """
    
    MIN_TITLE_LENGTH = 3
    MAX_TITLE_LENGTH = 200
    MIN_DURATION = 10
    MAX_DURATION = 7200
    MIN_OPTIONS = 2
    MAX_OPTIONS = 10
    MIN_QUESTIONS = 1
    MAX_QUESTIONS = 100
    MIN_POINTS = 1
    MAX_POINTS = 100
    
    VALID_STATUSES = ["APPROVED", "REJECTED"]
    EMAIL_REGEX = r"^[\w\.+-]+@[\w\.-]+\.\w+$"  # dozvoljen i "+" (npr. ime+igrac@gmail.com)

    @staticmethod
    def validate_quiz_creation(data: dict) -> Optional[Tuple]:
        """
        Validacija podataka za kreiranje kviza.
        Vraca None ako je sve OK, inace tuple (response, status_code).
        """
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        title = data.get("title") or data.get("name")
        if not title or not str(title).strip():
            return jsonify({"error": "Quiz title is required"}), 400

        title = str(title).strip()
        if len(title) < QuizValidation.MIN_TITLE_LENGTH:
            return jsonify({
                "error": f"Title must be at least {QuizValidation.MIN_TITLE_LENGTH} characters"
            }), 400
        if len(title) > QuizValidation.MAX_TITLE_LENGTH:
            return jsonify({
                "error": f"Title must not exceed {QuizValidation.MAX_TITLE_LENGTH} characters"
            }), 400

        duration = data.get("duration") or data.get("time_limit")
        if duration is None:
            return jsonify({"error": "Quiz duration is required"}), 400

        try:
            duration = int(duration)
        except (ValueError, TypeError):
            return jsonify({"error": "Duration must be a valid number"}), 400

        if duration < QuizValidation.MIN_DURATION:
            return jsonify({
                "error": f"Duration must be at least {QuizValidation.MIN_DURATION} seconds"
            }), 400
        if duration > QuizValidation.MAX_DURATION:
            return jsonify({
                "error": f"Duration must not exceed {QuizValidation.MAX_DURATION} seconds (2 hours)"
            }), 400

        author_id = data.get("author_id") or data.get("authorId")
        if author_id is None:
            return jsonify({"error": "Author ID is required"}), 400

        try:
            author_id = int(author_id)
            if author_id <= 0:
                return jsonify({"error": "Author ID must be a positive number"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Author ID must be a valid number"}), 400

        questions = data.get("questions")
        if not questions or not isinstance(questions, list):
            return jsonify({"error": "At least one question is required"}), 400

        if len(questions) < QuizValidation.MIN_QUESTIONS:
            return jsonify({
                "error": f"Quiz must have at least {QuizValidation.MIN_QUESTIONS} question(s)"
            }), 400
        if len(questions) > QuizValidation.MAX_QUESTIONS:
            return jsonify({
                "error": f"Quiz must not exceed {QuizValidation.MAX_QUESTIONS} questions"
            }), 400

        for idx, question in enumerate(questions):
            error = QuizValidation._validate_question(question, idx)
            if error:
                return error

        return None

    @staticmethod
    def _validate_question(question: dict, index: int) -> Optional[Tuple]:
        """
        Validacija pojedinačnog pitanja.
        """
        prefix = f"Question {index + 1}"

        if not isinstance(question, dict):
            return jsonify({"error": f"{prefix}: Invalid question format"}), 400

        text = question.get("text") or question.get("question")
        if not text or not str(text).strip():
            return jsonify({"error": f"{prefix}: Question text is required"}), 400

        text = str(text).strip()
        if len(text) < 3:
            return jsonify({
                "error": f"{prefix}: Question text must be at least 3 characters"
            }), 400
        if len(text) > 1000:
            return jsonify({
                "error": f"{prefix}: Question text must not exceed 1000 characters"
            }), 400

        options = question.get("options")
        if not options or not isinstance(options, list):
            return jsonify({"error": f"{prefix}: Options are required"}), 400

        valid_options = [str(opt).strip() for opt in options if opt and str(opt).strip()]

        if len(valid_options) < QuizValidation.MIN_OPTIONS:
            return jsonify({
                "error": f"{prefix}: At least {QuizValidation.MIN_OPTIONS} non-empty options are required"
            }), 400

        if len(valid_options) > QuizValidation.MAX_OPTIONS:
            return jsonify({
                "error": f"{prefix}: Maximum {QuizValidation.MAX_OPTIONS} options allowed"
            }), 400

        if len(valid_options) != len(set(opt.lower() for opt in valid_options)):
            return jsonify({"error": f"{prefix}: Duplicate options are not allowed"}), 400

        for opt in valid_options:
            if len(opt) > 500:
                return jsonify({
                    "error": f"{prefix}: Option text must not exceed 500 characters"
                }), 400

        correct_answers = question.get("correct_answers")
        if correct_answers is None:
            answer = question.get("answer")
            correct_answers = [str(answer)] if answer is not None else []

        if not isinstance(correct_answers, list):
            return jsonify({
                "error": f"{prefix}: correct_answers must be an array"
            }), 400

        valid_correct = [str(ans).strip() for ans in correct_answers if ans and str(ans).strip()]

        if len(valid_correct) == 0:
            return jsonify({
                "error": f"{prefix}: At least one correct answer is required"
            }), 400

        for ans in valid_correct:
            if ans not in valid_options:
                return jsonify({
                    "error": f"{prefix}: Correct answer '{ans}' must be one of the provided options"
                }), 400

        points = question.get("points", 1)
        try:
            points = int(points)
        except (ValueError, TypeError):
            return jsonify({"error": f"{prefix}: Points must be a valid number"}), 400

        if points < QuizValidation.MIN_POINTS:
            return jsonify({
                "error": f"{prefix}: Points must be at least {QuizValidation.MIN_POINTS}"
            }), 400
        if points > QuizValidation.MAX_POINTS:
            return jsonify({
                "error": f"{prefix}: Points must not exceed {QuizValidation.MAX_POINTS}"
            }), 400

        return None 

    @staticmethod
    def validate_status_update(data: dict) -> Optional[Tuple]:
        """
        Validacija promene statusa kviza (approve/reject).
        """
        if not data:
            return jsonify({"error": "Request body is required"}), 400

        status = data.get("status")
        if not status:
            return jsonify({"error": "Status is required"}), 400

        status = str(status).upper()
        if status not in QuizValidation.VALID_STATUSES:
            return jsonify({
                "error": f"Status must be one of: {', '.join(QuizValidation.VALID_STATUSES)}"
            }), 400

        if status == "REJECTED":
            reason = data.get("rejection_reason", "")
            if not reason or not str(reason).strip():
                return jsonify({
                    "error": "Rejection reason is required when rejecting a quiz"
                }), 400
            if len(str(reason).strip()) < 5:
                return jsonify({
                    "error": "Rejection reason must be at least 5 characters"
                }), 400
            if len(str(reason).strip()) > 500:
                return jsonify({
                    "error": "Rejection reason must not exceed 500 characters"
                }), 400

        return None

    @staticmethod
    def validate_quiz_submission(data: dict, total_questions: int) -> Optional[Tuple]:
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
                return jsonify({"error": f"Answer {idx + 1}: Invalid format"}), 400

            question_index = answer.get("question_index")
            if question_index is None:
                return jsonify({
                    "error": f"Answer {idx + 1}: question_index is required"
                }), 400

            try:
                question_index = int(question_index)
            except (ValueError, TypeError):
                return jsonify({
                    "error": f"Answer {idx + 1}: question_index must be a number"
                }), 400

            if question_index < 0 or question_index >= total_questions:
                return jsonify({
                    "error": f"Answer {idx + 1}: Invalid question_index {question_index}. Must be between 0 and {total_questions - 1}"
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

        user_email = data.get("user_email")
        if user_email:
            if not re.match(QuizValidation.EMAIL_REGEX, str(user_email)):
                return jsonify({"error": "Invalid user email format"}), 400

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
    def validate_quiz_id(quiz_id: str) -> Optional[Tuple]:
        """
        Validacija MongoDB ObjectId formata.
        """
        if not quiz_id:
            return jsonify({"error": "Quiz ID is required"}), 400
        
        if not re.match(r'^[a-fA-F0-9]{24}$', str(quiz_id)):
            return jsonify({"error": "Invalid quiz ID format"}), 400
        
        return None