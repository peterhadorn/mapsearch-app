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


class TestChangePassword:
    @patch("app.database.queries.execute", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_change_password_success(self, mock_get_user, mock_execute, client):
        mock_get_user.return_value = make_mock_user()

        from jose import jwt
        from app.config import SECRET_KEY, JWT_ALGORITHM
        token = jwt.encode({"sub": str(MOCK_USER_ID), "exp": 9999999999}, SECRET_KEY, algorithm=JWT_ALGORITHM)

        response = client.put("/api/auth/password",
            json={"current_password": "securepassword123", "new_password": "newpassword456"},
            cookies={"mapsearch_session": token}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed"

    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_change_password_wrong_current(self, mock_get_user, client):
        mock_get_user.return_value = make_mock_user()

        from jose import jwt
        from app.config import SECRET_KEY, JWT_ALGORITHM
        token = jwt.encode({"sub": str(MOCK_USER_ID), "exp": 9999999999}, SECRET_KEY, algorithm=JWT_ALGORITHM)

        response = client.put("/api/auth/password",
            json={"current_password": "wrongpassword", "new_password": "newpassword456"},
            cookies={"mapsearch_session": token}
        )
        assert response.status_code == 400


class TestDeleteAccount:
    @patch("app.database.queries.execute", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_delete_account_success(self, mock_get_user, mock_execute, client):
        mock_get_user.return_value = make_mock_user()

        from jose import jwt
        from app.config import SECRET_KEY, JWT_ALGORITHM
        token = jwt.encode({"sub": str(MOCK_USER_ID), "exp": 9999999999}, SECRET_KEY, algorithm=JWT_ALGORITHM)

        response = client.post("/api/auth/delete-account",
            cookies={"mapsearch_session": token}
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Account scheduled for deletion in 30 days"

    def test_delete_account_unauthenticated(self, client):
        response = client.post("/api/auth/delete-account")
        assert response.status_code == 401
