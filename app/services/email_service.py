"""SMTP email service for password reset and transactional emails."""

import logging
import smtplib
from email.message import EmailMessage

from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM

logger = logging.getLogger("mapsearch.email")


def send_reset_email(to_email: str, reset_url: str):
    """Send a password reset email via SMTP."""
    msg = EmailMessage()
    msg["Subject"] = "Reset your MapSearch password"
    msg["From"] = SMTP_FROM
    msg["To"] = to_email
    msg.set_content(
        f"You requested a password reset for your MapSearch account.\n\n"
        f"Click here to reset your password:\n{reset_url}\n\n"
        f"This link expires in 1 hour.\n\n"
        f"If you didn't request this, ignore this email."
    )

    if not SMTP_HOST:
        logger.warning("SMTP not configured — skipping email to %s", to_email)
        return

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

    logger.info("Reset email sent to %s", to_email)
