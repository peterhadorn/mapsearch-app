"""Tests for credits router — packs, checkout, webhook, balance."""

from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app
from app.routers.auth import require_current_user
from tests.conftest import make_mock_user, MOCK_USER_ID


def _override_auth(user=None):
    """Override require_current_user dependency to return a mock user."""
    if user is None:
        user = make_mock_user()

    async def _mock_user():
        return user

    app.dependency_overrides[require_current_user] = _mock_user
    return user


def _clear_auth():
    app.dependency_overrides.pop(require_current_user, None)


class TestListPacks:
    def test_list_packs_returns_4(self, client):
        resp = client.get("/api/credits/packs")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["packs"]) == 4
        pack_ids = [p["id"] for p in data["packs"]]
        assert pack_ids == ["starter", "growth", "pro", "agency"]


class TestCheckout:
    @patch("app.routers.credits.stripe")
    def test_checkout_creates_session(self, mock_stripe, client):
        _override_auth()
        try:
            mock_session = MagicMock()
            mock_session.url = "https://checkout.stripe.com/test_session"
            mock_stripe.checkout.Session.create.return_value = mock_session

            resp = client.post("/api/credits/checkout", json={"pack_id": "starter"})

            assert resp.status_code == 200
            assert resp.json()["checkout_url"] == "https://checkout.stripe.com/test_session"
            mock_stripe.checkout.Session.create.assert_called_once()
        finally:
            _clear_auth()

    def test_checkout_invalid_pack_returns_400(self, client):
        _override_auth()
        try:
            resp = client.post("/api/credits/checkout", json={"pack_id": "nonexistent"})
            assert resp.status_code == 400
        finally:
            _clear_auth()

    def test_checkout_requires_auth(self):
        from fastapi.testclient import TestClient
        fresh_client = TestClient(app)

        resp = fresh_client.post("/api/credits/checkout", json={"pack_id": "starter"})
        assert resp.status_code == 401


class TestWebhook:
    @patch("app.routers.credits.add_credits", new_callable=AsyncMock)
    @patch("app.routers.credits.stripe")
    def test_webhook_valid_adds_credits(self, mock_stripe, mock_add_credits, client):
        mock_event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {
                        "user_id": str(MOCK_USER_ID),
                        "pack_id": "starter",
                        "credits": "1000",
                    },
                    "payment_intent": "pi_test_123",
                }
            }
        }
        mock_stripe.Webhook.construct_event.return_value = mock_event

        resp = client.post(
            "/api/credits/webhook",
            content=b'{"test": "payload"}',
            headers={"stripe-signature": "test_sig"},
        )

        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        mock_add_credits.assert_called_once()
        call_args = mock_add_credits.call_args
        assert call_args[0][1] == 1000
        assert call_args[1]["stripe_payment_id"] == "pi_test_123"

    @patch("app.routers.credits.stripe")
    def test_webhook_invalid_signature_returns_400(self, mock_stripe, client):
        mock_stripe.Webhook.construct_event.side_effect = ValueError("Invalid signature")
        mock_stripe.error = MagicMock()
        mock_stripe.error.SignatureVerificationError = type("SignatureVerificationError", (Exception,), {})

        resp = client.post(
            "/api/credits/webhook",
            content=b'{"bad": "payload"}',
            headers={"stripe-signature": "bad_sig"},
        )

        assert resp.status_code == 400


class TestBalance:
    @patch("app.routers.credits.get_balance", new_callable=AsyncMock)
    def test_balance_returns_credits(self, mock_get_balance, client):
        user = make_mock_user(credits=5000)
        _override_auth(user)
        try:
            mock_get_balance.return_value = 5000

            resp = client.get("/api/credits/balance")
            assert resp.status_code == 200
            assert resp.json()["credits"] == 5000
        finally:
            _clear_auth()
