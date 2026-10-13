"""
Internal authentication.

The Quiz Service is never called by the browser. Only the main server calls it, and it must:
  - send the shared secret in the X-Internal-Key header,
  - forward the logged-in user (taken from the verified JWT) in X-User-* headers.

X-User-Name is percent-encoded by the main server (urllib.parse.quote), because HTTP
headers cannot carry characters like "Č" or "Đ" directly.
"""

import hmac
from dataclasses import dataclass
from functools import wraps
from urllib.parse import unquote

from flask import current_app, g, request

from app.domain.enums.role import Role
from app.domain.exceptions import ForbiddenError, UnauthorizedError

INTERNAL_KEY_HEADER = "X-Internal-Key"
USER_ID_HEADER = "X-User-Id"
USER_ROLE_HEADER = "X-User-Role"
USER_NAME_HEADER = "X-User-Name"
USER_EMAIL_HEADER = "X-User-Email"


@dataclass(frozen=True)
class RequestUser:
    """User on whose behalf the main server is calling the Quiz Service."""

    id: int
    role: Role
    full_name: str
    email: str


def require_internal_key() -> None:
    """
    before_request hook for every internal blueprint.
    Checks the shared key and stores the user context (if sent) in flask.g.
    """
    expected = current_app.config["INTERNAL_API_KEY"]
    provided = request.headers.get(INTERNAL_KEY_HEADER, "")

    if not expected or not provided or not hmac.compare_digest(provided.encode(), expected.encode()):
        raise UnauthorizedError("Invalid or missing internal API key")

    g.current_user = _read_user_context()


def _read_user_context() -> RequestUser | None:
    raw_id = request.headers.get(USER_ID_HEADER)
    raw_role = request.headers.get(USER_ROLE_HEADER)

    # Calls without a user (e.g. system calls) are allowed; endpoints that need a user use get_current_user().
    if raw_id is None and raw_role is None:
        return None

    try:
        user_id = int(raw_id)
        role = Role(raw_role)
    except (TypeError, ValueError):
        raise UnauthorizedError("Invalid user context headers")

    if user_id <= 0:
        raise UnauthorizedError("Invalid user context headers")

    return RequestUser(
        id=user_id,
        role=role,
        full_name=unquote(request.headers.get(USER_NAME_HEADER, "")).strip(),
        email=request.headers.get(USER_EMAIL_HEADER, "").strip(),
    )


def get_current_user() -> RequestUser:
    """Returns the user forwarded by the main server, or raises 401 if there is none."""
    user = g.get("current_user")
    if user is None:
        raise UnauthorizedError("User context is missing")
    return user


def roles_required(*roles: Role):
    """Allows the endpoint only for the given roles (second line of defense after the main server)."""

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            user = get_current_user()
            if user.role not in roles:
                raise ForbiddenError("Insufficient role for this action")
            return fn(*args, **kwargs)

        return decorator

    return wrapper
