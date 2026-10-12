from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify
from app.Domain.enums.role import Role

def role_required(*roles: Role):
    """
    Decorator for role-based access control.
    A "role" field coming from the token is expected in the JWT.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                verify_jwt_in_request()
                claims = get_jwt()
                user_role = claims.get("role")

                if user_role not in [r.value if isinstance(r, Role) else r for r in roles]:
                    return jsonify({"message": "Access denied: insufficient role"}), 403
            except Exception as e:
                return jsonify({"message": f"Authentication failed: {str(e)}"}), 401

            return fn(*args, **kwargs)
        return decorator
    return wrapper