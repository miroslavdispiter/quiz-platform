"""
Global error handlers.

Every error leaves the service in the same JSON shape, which the main server forwards to the client:
    {"error": {"code": "...", "message": "...", "details": ...}}
"""

import logging
from typing import Any

from bson.errors import InvalidId
from flask import Flask, jsonify
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.domain.exceptions import DomainError

logger = logging.getLogger(__name__)


def error_response(status_code: int, code: str, message: str, details: Any = None):
    body = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return jsonify(body), status_code


def _format_validation_errors(exc: ValidationError) -> list[dict]:
    return [
        {
            "field": ".".join(str(part) for part in err["loc"]),
            "message": err["msg"],
        }
        for err in exc.errors(include_url=False)
    ]


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(DomainError)
    def handle_domain_error(exc: DomainError):
        return error_response(exc.status_code, exc.code, exc.message, exc.details)

    @app.errorhandler(ValidationError)
    def handle_validation_error(exc: ValidationError):
        return error_response(400, "VALIDATION_ERROR", "Invalid request data", _format_validation_errors(exc))

    @app.errorhandler(InvalidId)
    def handle_invalid_id(exc: InvalidId):
        return error_response(400, "INVALID_ID", "Invalid id format")

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        code = (exc.name or "HTTP_ERROR").upper().replace(" ", "_")
        return error_response(exc.code or 500, code, exc.description or exc.name)

    @app.errorhandler(Exception)
    def handle_unexpected_error(exc: Exception):
        logger.exception("Unhandled error")
        return error_response(500, "INTERNAL_ERROR", "Unexpected server error")
