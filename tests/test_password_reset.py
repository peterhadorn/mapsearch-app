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
