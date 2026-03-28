"""Test configuration — set env vars and mock DB before any app imports."""

import os
import sys
import uuid
from datetime import datetime
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock

import pytest

# Set required env vars BEFORE importing the app
os.environ.setdefault("DATAFORSEO_LOGIN", "test")
os.environ.setdefault("DATAFORSEO_PASSWORD", "test")
os.environ.setdefault("MAPSEARCH_DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_test_fake")
os.environ.setdefault("MAPSEARCH_SECRET_KEY", "test-secret-key-for-jwt-signing-minimum-length")
os.environ["MAPSEARCH_ENV"] = "test"

# Mock asyncpg before any app imports — it may not be installable on this Python version
if "asyncpg" not in sys.modules:
    sys.modules["asyncpg"] = MagicMock()

from fastapi.testclient import TestClient
from app.main import app


MOCK_USER_ID = uuid.uuid4()
MOCK_USER_EMAIL = "test@example.com"


def make_mock_user(
    user_id=None,
    email=MOCK_USER_EMAIL,
    password_hash=None,
    credits=99,
    locale="en",
):
    """Create a dict that behaves like an asyncpg Record (supports dict-style access)."""
    user_id = user_id or MOCK_USER_ID
    if password_hash is None:
        from passlib.context import CryptContext
        password_hash = CryptContext(schemes=["bcrypt"], deprecated="auto").hash("securepassword123")

    class MockRecord(dict):
        def __getitem__(self, key):
            return super().__getitem__(key)

    return MockRecord({
        "id": user_id,
        "email": email,
        "password_hash": password_hash,
        "name": None,
        "google_id": None,
        "credits_remaining": credits,
        "locale": locale,
        "stripe_customer_id": None,
        "created_at": datetime(2026, 1, 1),
        "last_login_at": None,
        "deleted_at": None,
    })


@pytest.fixture
def mock_user():
    return make_mock_user()


@pytest.fixture
def client():
    """FastAPI TestClient with rate limiting disabled."""
    app.state.limiter._disabled = True
    return TestClient(app)
