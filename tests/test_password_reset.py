"""Tests for password reset flow — token generation, email, reset."""

import hashlib
import secrets
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta, timezone

import pytest

from tests.conftest import make_mock_user, MOCK_USER_ID, MOCK_USER_EMAIL


class TestEmailService:
    @patch("app.services.email_service.SMTP_HOST", "smtp.test.com")
    @patch("app.services.email_service.SMTP_PORT", 587)
    @patch("app.services.email_service.SMTP_USER", "testuser")
    @patch("app.services.email_service.SMTP_PASSWORD", "testpass")
    @patch("app.services.email_service.smtplib.SMTP")
    def test_send_reset_email(self, mock_smtp_cls):
        mock_server = MagicMock()
        mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

        from app.services.email_service import send_reset_email
        send_reset_email("test@example.com", "https://mapsearch.app/reset-password?token=abc123")

        mock_server.send_message.assert_called_once()

    @patch("app.services.email_service.SMTP_HOST", "")
    def test_send_reset_email_skips_when_no_smtp(self):
        """When SMTP_HOST is empty, email is silently skipped (dev/test mode)."""
        from app.services.email_service import send_reset_email
        send_reset_email("test@example.com", "https://mapsearch.app/reset-password?token=abc123")


class TestForgotPassword:
    @patch("app.routers.auth.queries.get_user_by_email", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.create_reset_token", new_callable=AsyncMock)
    @patch("app.routers.auth.send_reset_email")
    def test_forgot_password_sends_email(self, mock_send, mock_create_token, mock_get_user, client):
        mock_get_user.return_value = make_mock_user()
        mock_create_token.return_value = None

        response = client.post("/api/auth/forgot-password", json={"email": MOCK_USER_EMAIL})
        assert response.status_code == 200
        assert response.json()["message"] == "If that email exists, a reset link has been sent"
        mock_send.assert_called_once()

    @patch("app.routers.auth.queries.get_user_by_email", new_callable=AsyncMock)
    def test_forgot_password_unknown_email_still_200(self, mock_get_user, client):
        mock_get_user.return_value = None
        response = client.post("/api/auth/forgot-password", json={"email": "nobody@example.com"})
        assert response.status_code == 200
        assert response.json()["message"] == "If that email exists, a reset link has been sent"


class TestResetPassword:
    @patch("app.routers.auth.queries.get_valid_reset_token", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.update_user_password", new_callable=AsyncMock)
    @patch("app.routers.auth.queries.mark_token_used", new_callable=AsyncMock)
    def test_reset_password_success(self, mock_mark, mock_update, mock_get_token, client):
        mock_get_token.return_value = {
            "id": MOCK_USER_ID,
            "user_id": MOCK_USER_ID,
            "token_hash": "fakehash",
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            "used_at": None,
        }
        mock_update.return_value = None
        mock_mark.return_value = None

        response = client.post("/api/auth/reset-password", json={
            "token": "valid-token",
            "new_password": "newpassword123"
        })
        assert response.status_code == 200
        mock_update.assert_called_once()
        mock_mark.assert_called_once()

    @patch("app.routers.auth.queries.get_valid_reset_token", new_callable=AsyncMock)
    def test_reset_password_invalid_token(self, mock_get_token, client):
        mock_get_token.return_value = None
        response = client.post("/api/auth/reset-password", json={
            "token": "invalid-token",
            "new_password": "newpassword123"
        })
        assert response.status_code == 400
