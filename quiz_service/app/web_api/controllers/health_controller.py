from flask import Blueprint, jsonify

from app.extensions.mongo import mongo

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    """Public liveness check: is the service running and is MongoDB reachable."""
    mongo_up = mongo.ping()
    body = {
        "status": "ok" if mongo_up else "degraded",
        "service": "quiz-service",
        "mongo": "up" if mongo_up else "down",
    }
    return jsonify(body), 200 if mongo_up else 503
