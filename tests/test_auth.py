"""Tests for auth endpoints — signup, login, logout, me."""

from unittest.mock import AsyncMock, patch

from fastapi import Response
from jose import jwt

from app.config import JWT_ALGORITHM, JWT_COOKIE_NAME, SECRET_KEY
from app.routers.auth import _create_token, _set_session_cookie
from tests.conftest import make_mock_user


class TestAuthHelpers:
    def test_create_token_encodes_user_id(self):
        token = _create_token("user-123")

        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])

        assert payload["sub"] == "user-123"
        assert "exp" in payload

    def test_set_session_cookie_uses_expected_flags(self):
        response = Response()

        _set_session_cookie(response, "token-abc")

        cookie_header = response.headers.get("set-cookie", "")
        assert JWT_COOKIE_NAME in cookie_header
        assert "token-abc" in cookie_header
        assert "HttpOnly" in cookie_header
        assert "SameSite=lax" in cookie_header


class TestSignup:
    @patch("app.routers.auth.queries")
    def test_signup_creates_user_with_99_credits(self, mock_queries, client):
        new_user = make_mock_user()
        mock_queries.get_user_by_email = AsyncMock(return_value=None)
        mock_queries.create_user = AsyncMock(return_value=new_user)

        resp = client.post("/api/auth/signup", json={
            "email": "new@example.com",
            "password": "securepassword123",
        })

        assert resp.status_code == 201
        data = resp.json()
        assert data["credits_remaining"] == 99
        assert data["email"] == new_user["email"]
        assert "id" in data
        mock_queries.create_user.assert_called_once()

    @patch("app.routers.auth.queries")
    def test_signup_duplicate_email_returns_409(self, mock_queries, client):
        mock_queries.get_user_by_email = AsyncMock(return_value=make_mock_user())

        resp = client.post("/api/auth/signup", json={
            "email": "existing@example.com",
            "password": "securepassword123",
        })

        assert resp.status_code == 409

    @patch("app.routers.auth.queries")
    def test_signup_short_password_returns_422(self, mock_queries, client):
        resp = client.post("/api/auth/signup", json={
            "email": "new@example.com",
            "password": "short",
        })

        assert resp.status_code == 422

    @patch("app.routers.auth.queries")
    def test_signup_sets_httponly_cookie(self, mock_queries, client):
        new_user = make_mock_user()
        mock_queries.get_user_by_email = AsyncMock(return_value=None)
        mock_queries.create_user = AsyncMock(return_value=new_user)

        resp = client.post("/api/auth/signup", json={
            "email": "new@example.com",
            "password": "securepassword123",
        })

        assert resp.status_code == 201
        cookie_header = resp.headers.get("set-cookie", "")
        assert "mapsearch_session" in cookie_header
        assert "httponly" in cookie_header.lower()


class TestLogin:
    @patch("app.routers.auth.queries")
    def test_login_returns_session_cookie(self, mock_queries, client):
        user = make_mock_user()
        mock_queries.get_user_by_email = AsyncMock(return_value=user)

        resp = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "securepassword123",
        })

        assert resp.status_code == 200
        cookie_header = resp.headers.get("set-cookie", "")
        assert "mapsearch_session" in cookie_header
        assert "httponly" in cookie_header.lower()

    @patch("app.routers.auth.queries")
    def test_login_wrong_password_returns_401(self, mock_queries, client):
        user = make_mock_user()
        mock_queries.get_user_by_email = AsyncMock(return_value=user)

        resp = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword123",
        })

        assert resp.status_code == 401

    @patch("app.routers.auth.queries")
    def test_login_nonexistent_email_returns_401(self, mock_queries, client):
        mock_queries.get_user_by_email = AsyncMock(return_value=None)

        resp = client.post("/api/auth/login", json={
            "email": "noone@example.com",
            "password": "securepassword123",
        })

        assert resp.status_code == 401


class TestMe:
    @patch("app.routers.auth.queries")
    def test_me_returns_current_user(self, mock_queries, client):
        user = make_mock_user()
        mock_queries.get_user_by_email = AsyncMock(return_value=None)
        mock_queries.create_user = AsyncMock(return_value=user)

        # First signup to get a session cookie
        signup_resp = client.post("/api/auth/signup", json={
            "email": "new@example.com",
            "password": "securepassword123",
        })
        assert signup_resp.status_code == 201

        # Now call /me — the TestClient carries cookies automatically
        mock_queries.get_user_by_id = AsyncMock(return_value=user)
        me_resp = client.get("/api/auth/me")

        assert me_resp.status_code == 200
        data = me_resp.json()
        assert data["email"] == user["email"]
        assert data["credits_remaining"] == 99

    def test_me_without_auth_returns_401(self, client):
        # Fresh client with no cookies
        from fastapi.testclient import TestClient
        from app.main import app
        fresh_client = TestClient(app)

        resp = fresh_client.get("/api/auth/me")
        assert resp.status_code == 401


class TestLogout:
    @patch("app.routers.auth.queries")
    def test_logout_clears_cookie(self, mock_queries, client):
        user = make_mock_user()
        mock_queries.get_user_by_email = AsyncMock(return_value=None)
        mock_queries.create_user = AsyncMock(return_value=user)

        # Signup first
        client.post("/api/auth/signup", json={
            "email": "new@example.com",
            "password": "securepassword123",
        })

        # Logout
        resp = client.post("/api/auth/logout")
        assert resp.status_code == 200
        assert resp.json()["message"] == "Logged out"

        # Cookie should be cleared — set-cookie with max-age=0 or empty value
        cookie_header = resp.headers.get("set-cookie", "")
        assert "mapsearch_session" in cookie_header
