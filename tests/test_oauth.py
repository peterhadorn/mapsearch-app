"""Tests for Google OAuth2 endpoints."""

from unittest.mock import AsyncMock, MagicMock, patch
from urllib.parse import urlparse, parse_qs

from tests.conftest import make_mock_user


class TestGoogleLogin:
    def test_google_login_redirects_with_state(self, client):
        resp = client.get("/api/auth/google", follow_redirects=False)

        assert resp.status_code == 307
        location = resp.headers["location"]
        parsed = urlparse(location)
        params = parse_qs(parsed.query)

        assert parsed.hostname == "accounts.google.com"
        assert "state" in params
        assert params["client_id"][0] == "test-client-id"
        assert params["scope"][0] == "openid email profile"
        assert params["response_type"][0] == "code"

        # State cookie should be set
        cookie_header = resp.headers.get("set-cookie", "")
        assert "oauth_state" in cookie_header
        assert "httponly" in cookie_header.lower()


class TestGoogleCallback:
    def test_google_callback_invalid_state_returns_400(self, client):
        # Set a state cookie, then call with mismatched state
        client.cookies.set("oauth_state", "correct-state")
        resp = client.get(
            "/api/auth/google/callback?code=fake-code&state=wrong-state",
            follow_redirects=False,
        )
        assert resp.status_code == 400

    def test_google_callback_missing_state_cookie_returns_400(self, client):
        resp = client.get(
            "/api/auth/google/callback?code=fake-code&state=some-state",
            follow_redirects=False,
        )
        assert resp.status_code == 400

    @patch("app.routers.auth.queries")
    @patch("app.routers.auth.httpx.AsyncClient")
    def test_google_callback_creates_new_user(self, mock_httpx_cls, mock_queries, client):
        new_user = make_mock_user(email="googleuser@gmail.com")

        # Mock Google token exchange
        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = {"access_token": "fake-access-token"}

        # Mock Google userinfo
        mock_userinfo_resp = MagicMock()
        mock_userinfo_resp.json.return_value = {
            "sub": "google-id-12345",
            "email": "googleuser@gmail.com",
            "name": "Google User",
        }

        # Set up the async context manager mock
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_token_resp
        mock_client_instance.get.return_value = mock_userinfo_resp
        mock_httpx_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_httpx_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        # No existing user
        mock_queries.get_user_by_google_id = AsyncMock(return_value=None)
        mock_queries.get_user_by_email = AsyncMock(return_value=None)
        mock_queries.create_user = AsyncMock(return_value=new_user)

        client.cookies.set("oauth_state", "valid-state")
        resp = client.get(
            "/api/auth/google/callback?code=auth-code&state=valid-state",
            follow_redirects=False,
        )

        assert resp.status_code == 302
        assert resp.headers["location"] == "/"

        # Verify user was created with Google details
        mock_queries.create_user.assert_called_once_with(
            email="googleuser@gmail.com",
            password_hash=None,
            name="Google User",
            google_id="google-id-12345",
        )

        # Session cookie should be set
        cookie_header = resp.headers.get("set-cookie", "")
        assert "mapsearch_session" in cookie_header

    @patch("app.routers.auth.queries")
    @patch("app.routers.auth.httpx.AsyncClient")
    def test_google_callback_links_existing_email(self, mock_httpx_cls, mock_queries, client):
        existing_user = make_mock_user(email="existing@example.com")

        # Mock Google token exchange
        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = {"access_token": "fake-access-token"}

        # Mock Google userinfo
        mock_userinfo_resp = MagicMock()
        mock_userinfo_resp.json.return_value = {
            "sub": "google-id-99999",
            "email": "existing@example.com",
            "name": "Existing User",
        }

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_token_resp
        mock_client_instance.get.return_value = mock_userinfo_resp
        mock_httpx_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_httpx_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        # No user by google_id, but exists by email
        mock_queries.get_user_by_google_id = AsyncMock(return_value=None)
        mock_queries.get_user_by_email = AsyncMock(return_value=existing_user)
        mock_queries.link_google_id = AsyncMock(return_value=None)

        client.cookies.set("oauth_state", "valid-state")
        resp = client.get(
            "/api/auth/google/callback?code=auth-code&state=valid-state",
            follow_redirects=False,
        )

        assert resp.status_code == 302

        # Verify google_id was linked, not a new user created
        mock_queries.link_google_id.assert_called_once_with(
            existing_user["id"], "google-id-99999",
        )
        mock_queries.create_user.assert_not_called()

    @patch("app.routers.auth.queries")
    @patch("app.routers.auth.httpx.AsyncClient")
    def test_google_callback_token_exchange_failure_returns_400(
        self, mock_httpx_cls, mock_queries, client
    ):
        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 401
        mock_token_resp.json.return_value = {"error": "invalid_grant"}

        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_token_resp
        mock_httpx_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_httpx_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        client.cookies.set("oauth_state", "valid-state")
        resp = client.get(
            "/api/auth/google/callback?code=bad-code&state=valid-state",
            follow_redirects=False,
        )

        assert resp.status_code == 400
