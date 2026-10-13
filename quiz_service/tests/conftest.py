import pytest

from app import create_app

TEST_INTERNAL_KEY = "test-internal-key"


@pytest.fixture
def app():
    app = create_app(
        overrides={
            "TESTING": True,
            "INTERNAL_API_KEY": TEST_INTERNAL_KEY,
            "MONGO_DB_NAME": "quiz_db_test",
            "MONGO_TIMEOUT_MS": 300,
        }
    )
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def internal_headers():
    """Headers the main server sends: internal key + logged-in user."""
    return {
        "X-Internal-Key": TEST_INTERNAL_KEY,
        "X-User-Id": "7",
        "X-User-Role": "MODERATOR",
        "X-User-Name": "Mi%C5%A1o%20%C4%90uri%C4%87",  # "Mišo Đurić", percent-encoded
        "X-User-Email": "miso@example.com",
    }
