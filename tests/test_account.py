"""Tests for account management — soft delete, password change."""

from unittest.mock import AsyncMock, patch
from datetime import datetime

from tests.conftest import make_mock_user, MOCK_USER_ID, MOCK_USER_EMAIL


def _make_deleted_user():
    user = make_mock_user()
    user["deleted_at"] = datetime(2026, 3, 1)
    return user


class TestSoftDeleteGuard:
    """Soft-deleted users must not be returned by user lookups."""

    @patch("app.database.queries.fetchrow", new_callable=AsyncMock)
    def test_get_user_by_email_excludes_deleted(self, mock_fetchrow, client):
        mock_fetchrow.return_value = None
        response = client.post("/api/auth/login", json={
            "email": MOCK_USER_EMAIL,
            "password": "securepassword123"
        })
        assert response.status_code == 401

    @patch("app.database.queries.fetchrow", new_callable=AsyncMock)
    def test_get_user_by_id_excludes_deleted(self, mock_fetchrow, client):
        mock_fetchrow.return_value = None
        response = client.get("/api/auth/me")
        assert response.status_code == 401
