from flask import Blueprint

from app.web_api.middleware.internal_auth import require_internal_key

quiz_bp = Blueprint("quizzes", __name__)

# Every route in this blueprint is internal: only the main server (with X-Internal-Key) may call it.
quiz_bp.before_request(require_internal_key)

# TODO (celina 3): quiz routes - create, update, delete, mine, by status, published, details, review.
