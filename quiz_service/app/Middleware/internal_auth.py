from functools import wraps
from flask import request, jsonify
from app.config import Config


def check_internal_key():

    key = request.headers.get("X-Internal-Key")
    if not Config.INTERNAL_API_KEY or key != Config.INTERNAL_API_KEY:
        return jsonify({"error": "Access not allowed"}), 401


def get_current_user() -> dict:
    """The main server sends the logged-in user in headers (taken from the JWT)."""
    try:
        user_id = int(request.headers.get("X-User-Id", 0))
    except ValueError:
        user_id = 0
    return {
        "id": user_id,
        "role": request.headers.get("X-User-Role", ""),
    }


def role_required(*roles):
    """Same idea as role_required on the main server, but the role comes from the X-User-Role header."""
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user = get_current_user()
            if user["role"] not in [r.value for r in roles]:
                return jsonify({"error": "Access denied: insufficient role"}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
