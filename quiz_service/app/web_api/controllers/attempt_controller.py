from flask import Blueprint

from app.web_api.middleware.internal_auth import require_internal_key

attempt_bp = Blueprint("attempts", __name__)

# Every route in this blueprint is internal: only the main server (with X-Internal-Key) may call it.
attempt_bp.before_request(require_internal_key)

# TODO (celina 6-8): attempt routes - start attempt, submit answers (202), my attempts, leaderboard.
