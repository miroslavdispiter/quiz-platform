from typing import Any


class DomainError(Exception):
    """
    Base error for the Quiz Service.
    Services raise these errors; the web layer turns them into JSON responses
    (see app/web_api/error_handlers.py), so services never deal with HTTP.
    """

    status_code = 400
    code = "BAD_REQUEST"

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class UnauthorizedError(DomainError):
    """Request is not coming from the main server or the user context is missing."""

    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenError(DomainError):
    """User is known but is not allowed to perform the action."""

    status_code = 403
    code = "FORBIDDEN"


class NotFoundError(DomainError):
    """Requested quiz/attempt does not exist."""

    status_code = 404
    code = "NOT_FOUND"


class ConflictError(DomainError):
    """Action is not allowed in the current state (e.g. reviewing an already approved quiz)."""

    status_code = 409
    code = "CONFLICT"
