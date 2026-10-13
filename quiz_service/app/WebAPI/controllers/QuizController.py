from flask import Blueprint, jsonify, request
from app.Services.QuizService import QuizService
from app.Services.ResultService import ResultService
from app.WebAPI.validation.QuizValidation import QuizValidation
from app.Middleware.internal_auth import get_current_user, role_required
from app.Domain.enums.role import Role

quiz_bp = Blueprint("quizzes", __name__)
quiz_service = QuizService()
result_service = ResultService()


# CREATE QUIZ
@quiz_bp.route("", methods=["POST"])
@role_required(Role.MODERATOR)
def create_quiz():
    data = request.get_json(silent=True)

    error = QuizValidation.validate_quiz(data)
    if error:
        return jsonify({"error": error}), 400

    result, status = quiz_service.create_quiz(data, get_current_user())
    return jsonify(result), status


# EDIT QUIZ
@quiz_bp.route("/<quiz_id>", methods=["PUT"])
@role_required(Role.MODERATOR)
def update_quiz(quiz_id):
    data = request.get_json(silent=True)

    error = QuizValidation.validate_quiz(data)
    if error:
        return jsonify({"error": error}), 400

    result, status = quiz_service.update_quiz(quiz_id, data, get_current_user())
    return jsonify(result), status


# DELETE QUIZ
@quiz_bp.route("/<quiz_id>", methods=["DELETE"])
@role_required(Role.MODERATOR, Role.ADMIN)
def delete_quiz(quiz_id):
    result, status = quiz_service.delete_quiz(quiz_id, get_current_user())
    return jsonify(result), status


# ALL QUIZZES (admin)
@quiz_bp.route("", methods=["GET"])
@role_required(Role.ADMIN)
def get_all_quizzes():
    result, status = quiz_service.get_all_quizzes()
    return jsonify(result), status


# MY QUIZZES (moderator)
@quiz_bp.route("/mine", methods=["GET"])
@role_required(Role.MODERATOR)
def get_my_quizzes():
    result, status = quiz_service.get_my_quizzes(get_current_user())
    return jsonify(result), status


# APPROVED QUIZZES (everyone)
@quiz_bp.route("/published", methods=["GET"])
def get_published_quizzes():
    result, status = quiz_service.get_published_quizzes()
    return jsonify(result), status


# ONE QUIZ
@quiz_bp.route("/<quiz_id>", methods=["GET"])
def get_quiz(quiz_id):
    result, status = quiz_service.get_quiz(quiz_id, get_current_user())
    return jsonify(result), status


# APPROVE / REJECT
@quiz_bp.route("/<quiz_id>/review", methods=["PATCH"])
@role_required(Role.ADMIN)
def review_quiz(quiz_id):
    data = request.get_json(silent=True)

    error = QuizValidation.validate_review(data)
    if error:
        return jsonify({"error": error}), 400

    result, status = quiz_service.review_quiz(quiz_id, data)
    return jsonify(result), status


# SUBMIT ANSWERS (processing is asynchronous -> 202 Accepted)
@quiz_bp.route("/<quiz_id>/submit", methods=["POST"])
@role_required(Role.PLAYER)
def submit_answers(quiz_id):
    data = request.get_json(silent=True)

    error = QuizValidation.validate_submission(data)
    if error:
        return jsonify({"error": error}), 400

    result, status = result_service.submit_answers(quiz_id, data, get_current_user())
    return jsonify(result), status


# LEADERBOARD
@quiz_bp.route("/<quiz_id>/leaderboard", methods=["GET"])
def get_leaderboard(quiz_id):
    result, status = result_service.get_leaderboard(quiz_id)
    return jsonify(result), status
