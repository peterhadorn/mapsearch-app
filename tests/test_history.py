"""Tests for search history and credit transaction endpoints."""

from unittest.mock import AsyncMock, patch
from datetime import datetime
import uuid

from tests.conftest import make_mock_user, MOCK_USER_ID


def _make_auth_cookie():
    from jose import jwt
    from app.config import SECRET_KEY, JWT_ALGORITHM
    return {"mapsearch_session": jwt.encode(
        {"sub": str(MOCK_USER_ID), "exp": 9999999999}, SECRET_KEY, algorithm=JWT_ALGORITHM
    )}


class TestCreditTransactions:
    @patch("app.routers.auth.queries.get_user_by_id", new_callable=AsyncMock)
    @patch("app.database.queries.get_credit_transactions", new_callable=AsyncMock)
    @patch("app.database.queries.count_credit_transactions", new_callable=AsyncMock)
    def test_list_transactions(self, mock_count, mock_txns, mock_get_user, client):
        mock_get_user.return_value = make_mock_user()
        mock_count.return_value = 2
        mock_txns.return_value = [
            {"id": uuid.uuid4(), "amount": -10, "type": "search", "reference_id": None,
             "stripe_payment_id": None, "created_at": datetime(2026, 3, 28)},
            {"id": uuid.uuid4(), "amount": 1000, "type": "purchase", "reference_id": None,
             "stripe_payment_id": "pi_test", "created_at": datetime(2026, 3, 27)},
        ]

        response = client.get("/api/credits/transactions", cookies=_make_auth_cookie())
        assert response.status_code == 200
        data = response.json()
        assert len(data["transactions"]) == 2
        assert data["total"] == 2
        assert data["has_next"] is False

    def test_transactions_unauthenticated(self, client):
        response = client.get("/api/credits/transactions")
        assert response.status_code == 401
