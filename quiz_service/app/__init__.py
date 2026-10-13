from flask import Flask
from app.Middleware.internal_auth import check_internal_key
from app.WebAPI.controllers.QuizController import quiz_bp


def create_app():
    app = Flask(__name__)

    # Every request must come from the main server (X-Internal-Key header)
    app.before_request(check_internal_key)

    app.register_blueprint(quiz_bp, url_prefix="/quizzes")

    return app
