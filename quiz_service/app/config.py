import os
from collections.abc import Mapping
from typing import Any

from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Environment variable {name} must be an integer, got '{value}'") from exc


class Config:
    """Quiz Service configuration, loaded from environment variables (.env)."""

    # --- Server ---
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = _get_int("PORT", 5001)
    DEBUG = _get_bool("FLASK_DEBUG", False)
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    JSON_SORT_KEYS = False

    # --- MongoDB (DB2) ---
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "quiz_db")
    MONGO_TIMEOUT_MS = _get_int("MONGO_TIMEOUT_MS", 3000)

    # --- Communication with the main server ---
    MAIN_SERVER_URL = os.getenv("MAIN_SERVER_URL", "http://localhost:5000").rstrip("/")
    INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")
    REQUEST_TIMEOUT_SECONDS = _get_int("REQUEST_TIMEOUT_SECONDS", 5)

    # --- Asynchronous grading (processes) ---
    GRADING_WORKERS = _get_int("GRADING_WORKERS", 2)
    GRADING_DELAY_SECONDS = _get_int("GRADING_DELAY_SECONDS", 10)

    # --- Email ---
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = _get_int("SMTP_PORT", 587)
    EMAIL_USER = os.getenv("EMAIL_USER", "")
    EMAIL_PASS = os.getenv("EMAIL_PASS", "")
    EMAIL_FROM = os.getenv("EMAIL_FROM", "") or os.getenv("EMAIL_USER", "")


def validate_config(config: Mapping[str, Any]) -> None:
    """Fails fast at startup if a required setting is missing or invalid."""
    internal_key = config.get("INTERNAL_API_KEY")
    if not internal_key or internal_key == "CHANGE_ME":
        raise RuntimeError(
            "INTERNAL_API_KEY is not set. Put the same value in quiz_service/.env and server/.env."
        )
    if config.get("GRADING_WORKERS", 0) < 1:
        raise RuntimeError("GRADING_WORKERS must be at least 1.")
    if config.get("GRADING_DELAY_SECONDS", -1) < 0:
        raise RuntimeError("GRADING_DELAY_SECONDS cannot be negative.")
