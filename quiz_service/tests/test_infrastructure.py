"""Tests for celina 1: app factory, internal auth, error handlers, health check."""

import pytest
from flask import Blueprint, jsonify
from pydantic import BaseModel, Field

from app import create_app
from app.domain.enums.role import Role
from app.domain.exceptions import ConflictError, NotFoundError
from app.extensions.mongo import mongo
from app.web_api.middleware.internal_auth import get_current_user, require_internal_key, roles_required


@pytest.fixture
def probe_app(app):
    """Registers a small internal blueprint so the middleware and error handlers can be tested."""
    bp = Blueprint("probe", __name__)
    bp.before_request(require_internal_key)

    @bp.get("/me")
    def me():
        user = get_current_user()
        return jsonify(id=user.id, role=user.role.value, full_name=user.full_name, email=user.email)

    @bp.get("/admin-only")
    @roles_required(Role.ADMIN)
    def admin_only():
        return jsonify(ok=True)

    @bp.get("/not-found")
    def not_found():
        raise NotFoundError("Quiz not found")

    @bp.get("/conflict")
    def conflict():
        raise ConflictError("Quiz is not pending", details={"status": "APPROVED"})

    class Payload(BaseModel):
        title: str = Field(min_length=3)

    @bp.get("/invalid")
    def invalid():
        Payload.model_validate({"title": "a"})

    @bp.get("/crash")
    def crash():
        raise RuntimeError("boom")

    app.register_blueprint(bp, url_prefix="/probe")
    return app


@pytest.fixture
def probe(probe_app):
    return probe_app.test_client()


def test_missing_internal_key_is_rejected(probe):
    res = probe.get("/probe/me")
    assert res.status_code == 401
    assert res.get_json()["error"]["code"] == "UNAUTHORIZED"


def test_wrong_internal_key_is_rejected(probe, internal_headers):
    res = probe.get("/probe/me", headers={**internal_headers, "X-Internal-Key": "wrong"})
    assert res.status_code == 401


def test_user_context_is_read_and_name_is_decoded(probe, internal_headers):
    res = probe.get("/probe/me", headers=internal_headers)
    assert res.status_code == 200
    assert res.get_json() == {
        "id": 7,
        "role": "MODERATOR",
        "full_name": "Mišo Đurić",
        "email": "miso@example.com",
    }


def test_missing_user_context_is_401_only_where_user_is_needed(probe):
    res = probe.get("/probe/me", headers={"X-Internal-Key": "test-internal-key"})
    assert res.status_code == 401
    assert res.get_json()["error"]["message"] == "User context is missing"


@pytest.mark.parametrize("user_id, role", [("abc", "ADMIN"), ("5", "SUPERUSER"), ("-1", "ADMIN")])
def test_invalid_user_context_is_rejected(probe, internal_headers, user_id, role):
    res = probe.get("/probe/me", headers={**internal_headers, "X-User-Id": user_id, "X-User-Role": role})
    assert res.status_code == 401


def test_roles_required_forbids_other_roles(probe, internal_headers):
    assert probe.get("/probe/admin-only", headers=internal_headers).status_code == 403
    admin = {**internal_headers, "X-User-Role": "ADMIN"}
    assert probe.get("/probe/admin-only", headers=admin).status_code == 200


def test_domain_errors_have_uniform_shape(probe, internal_headers):
    res = probe.get("/probe/not-found", headers=internal_headers)
    assert res.status_code == 404
    assert res.get_json() == {"error": {"code": "NOT_FOUND", "message": "Quiz not found"}}

    res = probe.get("/probe/conflict", headers=internal_headers)
    assert res.status_code == 409
    assert res.get_json()["error"]["details"] == {"status": "APPROVED"}


def test_pydantic_validation_error_becomes_400(probe, internal_headers):
    res = probe.get("/probe/invalid", headers=internal_headers)
    body = res.get_json()
    assert res.status_code == 400
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"][0]["field"] == "title"


def test_unexpected_error_does_not_leak_details(probe, internal_headers):
    res = probe.get("/probe/crash", headers=internal_headers)
    assert res.status_code == 500
    assert res.get_json()["error"] == {"code": "INTERNAL_ERROR", "message": "Unexpected server error"}


def test_unknown_route_is_json_404(client):
    res = client.get("/does-not-exist")
    assert res.status_code == 404
    assert res.get_json()["error"]["code"] == "NOT_FOUND"


def test_quiz_and_attempt_blueprints_are_internal(app):
    # The routes come in later steps; here we only check that internal auth guards both blueprints.
    assert require_internal_key in app.before_request_funcs["quizzes"]
    assert require_internal_key in app.before_request_funcs["attempts"]


def test_health_reports_mongo_status(client, monkeypatch):
    monkeypatch.setattr(mongo, "ping", lambda: True)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json() == {"status": "ok", "service": "quiz-service", "mongo": "up"}

    monkeypatch.setattr(mongo, "ping", lambda: False)
    res = client.get("/health")
    assert res.status_code == 503
    assert res.get_json()["mongo"] == "down"


def test_app_refuses_to_start_without_internal_key():
    with pytest.raises(RuntimeError, match="INTERNAL_API_KEY"):
        create_app(overrides={"INTERNAL_API_KEY": ""})
