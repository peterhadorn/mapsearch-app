"""Tests for admin panel — access control and actions."""

from unittest.mock import AsyncMock, patch
from datetime import datetime
import uuid
import os

from tests.conftest import make_mock_user, MOCK_USER_ID, MOCK_USER_EMAIL


def _make_auth_cookie(email=None):
    """Create a JWT cookie for a specific user."""
    from jose import jwt
    from app.config import SECRET_KEY, JWT_ALGORITHM
    user_id = str(MOCK_USER_ID)
    return {"mapsearch_session": jwt.encode(
        {"sub": user_id, "exp": 9999999999}, SECRET_KEY, algorithm=JWT_ALGORITHM
    )}


def _make_admin_user():
    return make_mock_user(email=os.environ.get("ADMIN_EMAIL", "admin@test.com"))


def _make_regular_user():
    return make_mock_user(email="regular@example.com")


class TestAdminAccess:
    """Admin panel access control."""

    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_admin_page_loads_for_admin(self, mock_get_user, client):
        mock_get_user.return_value = _make_admin_user()
        with patch("app.database.queries.admin_get_stats", new_callable=AsyncMock) as mock_stats, \
             patch("app.database.queries.admin_get_users", new_callable=AsyncMock) as mock_users, \
             patch("app.database.queries.admin_count_users", new_callable=AsyncMock) as mock_count:
            mock_stats.return_value = {"total_users": 5, "total_searches": 100, "total_credits_sold": 5000, "estimated_revenue": 7.00}
            mock_users.return_value = []
            mock_count.return_value = 0
            response = client.get("/admin", cookies=_make_auth_cookie())
        assert response.status_code == 200

    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_admin_403_for_non_admin(self, mock_get_user, client):
        mock_get_user.return_value = _make_regular_user()
        response = client.get("/admin", cookies=_make_auth_cookie())
        assert response.status_code == 403

    def test_admin_redirects_unauthenticated(self, client):
        response = client.get("/admin", follow_redirects=False)
        assert response.status_code == 302


class TestAdminActions:
    """Admin credit adjustment and user deletion."""

    @patch("app.database.queries.admin_adjust_credits", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_adjust_credits(self, mock_get_user, mock_adjust, client):
        mock_get_user.return_value = _make_admin_user()
        mock_adjust.return_value = None
        target_user = uuid.uuid4()
        response = client.post("/admin/api/adjust-credits",
            data={"user_id": str(target_user), "amount": "500"},
            cookies=_make_auth_cookie(),
            follow_redirects=False
        )
        assert response.status_code == 303
        mock_adjust.assert_called_once_with(target_user, 500)

    @patch("app.database.queries.admin_delete_user", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_delete_user(self, mock_get_user, mock_delete, client):
        mock_get_user.return_value = _make_admin_user()
        mock_delete.return_value = None
        target_user = uuid.uuid4()
        response = client.post("/admin/api/delete-user",
            data={"user_id": str(target_user)},
            cookies=_make_auth_cookie(),
            follow_redirects=False
        )
        assert response.status_code == 303
        mock_delete.assert_called_once_with(target_user)

    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_delete_self_returns_400(self, mock_get_user, client):
        mock_get_user.return_value = _make_admin_user()
        response = client.post("/admin/api/delete-user",
            data={"user_id": str(MOCK_USER_ID)},
            cookies=_make_auth_cookie(),
        )
        assert response.status_code == 400

    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    def test_adjust_credits_403_for_non_admin(self, mock_get_user, client):
        mock_get_user.return_value = _make_regular_user()
        response = client.post("/admin/api/adjust-credits",
            data={"user_id": str(uuid.uuid4()), "amount": "100"},
            cookies=_make_auth_cookie(),
        )
        assert response.status_code == 403
