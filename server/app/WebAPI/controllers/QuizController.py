from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.Services.QuizService import QuizService
from app.Middleware.role_required import role_required
from app.Domain.enums.role import Role
from app.Extensions.socketio_ext import socketio

quiz_bp = Blueprint("quizzes", __name__)
quiz_service = QuizService()


def current_user_id() -> int:
    return int(get_jwt_identity())


# CREATE QUIZ -> admin gets it in real time
@quiz_bp.route("/", methods=["POST"], strict_slashes=False)
@jwt_required()
@role_required(Role.MODERATOR)
def create_quiz():
    data = request.get_json(silent=True)
    result, status = quiz_service.create_quiz(current_user_id(), data)

    if status == 201:
        socketio.emit("quiz_created", {
            "quiz_id": result["_id"],
            "title": result["title"],
            "message": f"New quiz \"{result['title']}\" by {result['author_name']} is waiting for approval",
        }, to=Role.ADMIN.value)

    return jsonify(result), status


# EDIT QUIZ -> goes back to the admin for approval
@quiz_bp.route("/<quiz_id>", methods=["PUT"])
@jwt_required()
@role_required(Role.MODERATOR)
def update_quiz(quiz_id):
    data = request.get_json(silent=True)
    result, status = quiz_service.update_quiz(current_user_id(), quiz_id, data)

    if status == 200:
        socketio.emit("quiz_created", {
            "quiz_id": result["_id"],
            "title": result["title"],
            "message": f"Quiz \"{result['title']}\" was edited and is waiting for approval",
        }, to=Role.ADMIN.value)

    return jsonify(result), status


# DELETE QUIZ (moderator - own quizzes, admin - all)
@quiz_bp.route("/<quiz_id>", methods=["DELETE"])
@jwt_required()
@role_required(Role.MODERATOR, Role.ADMIN)
def delete_quiz(quiz_id):
    result, status = quiz_service.delete_quiz(current_user_id(), quiz_id)

    if status == 200:
        socketio.emit("quiz_deleted", {"quiz_id": quiz_id, "title": result["title"]})

    return jsonify(result), status


# ALL QUIZZES (admin)
@quiz_bp.route("/", methods=["GET"], strict_slashes=False)
@jwt_required()
@role_required(Role.ADMIN)
def get_all_quizzes():
    result, status = quiz_service.get_all_quizzes(current_user_id())
    return jsonify(result), status


# MY QUIZZES (moderator)
@quiz_bp.route("/mine", methods=["GET"])
@jwt_required()
@role_required(Role.MODERATOR)
def get_my_quizzes():
    result, status = quiz_service.get_my_quizzes(current_user_id())
    return jsonify(result), status


# APPROVED QUIZZES (players)
@quiz_bp.route("/published", methods=["GET"])
@jwt_required()
def get_published_quizzes():
    result, status = quiz_service.get_published_quizzes(current_user_id())
    return jsonify(result), status


# ONE QUIZ (players get it without correct answers)
@quiz_bp.route("/<quiz_id>", methods=["GET"])
@jwt_required()
def get_quiz(quiz_id):
    result, status = quiz_service.get_quiz(current_user_id(), quiz_id)
    return jsonify(result), status


# APPROVE / REJECT -> moderator is notified, players see an approved quiz in real time
@quiz_bp.route("/<quiz_id>/review", methods=["PATCH"])
@jwt_required()
@role_required(Role.ADMIN)
def review_quiz(quiz_id):
    data = request.get_json(silent=True)
    result, status = quiz_service.review_quiz(current_user_id(), quiz_id, data)

    if status == 200:
        approved = result["status"] == "APPROVED"

        socketio.emit("quiz_reviewed", {
            "quiz_id": result["_id"],
            "title": result["title"],
            "status": result["status"],
            "rejection_reason": result["rejection_reason"],
            "message": f"Your quiz \"{result['title']}\" was " + ("approved" if approved else "rejected"),
        }, to=f"user_{result['author_id']}")

        if approved:
            socketio.emit("quiz_published", {
                "quiz_id": result["_id"],
                "title": result["title"],
                "message": f"New quiz available: \"{result['title']}\"",
            }, to=Role.PLAYER.value)

    return jsonify(result), status


# SUBMIT ANSWERS (processed asynchronously, result comes by email)
@quiz_bp.route("/<quiz_id>/submit", methods=["POST"])
@jwt_required()
@role_required(Role.PLAYER)
def submit_answers(quiz_id):
    data = request.get_json(silent=True)
    result, status = quiz_service.submit_answers(current_user_id(), quiz_id, data)
    return jsonify(result), status


# LEADERBOARD
@quiz_bp.route("/<quiz_id>/leaderboard", methods=["GET"])
@jwt_required()
def get_leaderboard(quiz_id):
    result, status = quiz_service.get_leaderboard(current_user_id(), quiz_id)
    return jsonify(result), status
