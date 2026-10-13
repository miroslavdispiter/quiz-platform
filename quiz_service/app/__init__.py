from typing import Any

from flask import Flask

from app.config import Config, validate_config
from app.extensions.mongo import mongo
from app.logging_config import configure_logging
from app.web_api.controllers.attempt_controller import attempt_bp
from app.web_api.controllers.health_controller import health_bp
from app.web_api.controllers.quiz_controller import quiz_bp
from app.web_api.error_handlers import register_error_handlers


def create_app(config_class: type[Config] = Config, overrides: dict[str, Any] | None = None) -> Flask:
    """
    Application factory for the Quiz Service.
    `overrides` lets tests change single settings without touching .env.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)
    if overrides:
        app.config.update(overrides)
    validate_config(app.config)

    configure_logging(app.config["LOG_LEVEL"])

    # Extensions
    mongo.init_app(app)
    # TODO (celina 2): create MongoDB indexes on startup (app/database/indexes.py).

    # Web layer
    register_error_handlers(app)
    app.register_blueprint(health_bp)
    app.register_blueprint(quiz_bp, url_prefix="/api/quizzes")
    app.register_blueprint(attempt_bp, url_prefix="/api/attempts")

    return app
