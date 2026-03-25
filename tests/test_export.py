"""Tests for export router — CSV download for search results."""

import uuid
from unittest.mock import AsyncMock, patch, call

import pytest

from tests.conftest import make_mock_user, MOCK_USER_ID
from app.main import app
from app.routers.auth import require_current_user
from fastapi.testclient import TestClient


SEARCH_ID = uuid.uuid4()
SCRAPE_CACHE_ID = uuid.uuid4()

MOCK_SEARCH = {
    "id": SEARCH_ID,
    "scrape_cache_id": SCRAPE_CACHE_ID,
    "filtered_result_count": 2,
}

MOCK_RESULTS = [
    {
        "business_name": "Acme Corp",
        "category": "Consulting",
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "country": "US",
        "phone": "555-1234",
        "email": "info@acme.com",
        "domain": "acme.com",
        "url": "https://acme.com",
        "rating": 4.5,
        "reviews_count": 100,
        "is_claimed": True,
        "verified": True,
        "photos_count": 10,
        "latitude": 40.7128,
        "longitude": -74.006,
        "google_maps_url": "https://maps.google.com/?cid=123",
        "price_level": "$$",
        "business_status": "OPERATIONAL",
        # Extra DB columns that should be ignored by extrasaction='ignore'
        "id": uuid.uuid4(),
        "scrape_cache_id": SCRAPE_CACHE_ID,
    },
    {
        "business_name": "Beta LLC",
        "category": "Retail",
        "address": "456 Oak Ave",
        "city": "Brooklyn",
        "state": "NY",
        "zip": "11201",
        "country": "US",
        "phone": "555-5678",
        "email": None,
        "domain": "beta.com",
        "url": "https://beta.com",
        "rating": 3.8,
        "reviews_count": 42,
        "is_claimed": False,
        "verified": False,
        "photos_count": 0,
        "latitude": 40.6782,
        "longitude": -73.9442,
        "google_maps_url": "https://maps.google.com/?cid=456",
        "price_level": "$",
        "business_status": "OPERATIONAL",
        "id": uuid.uuid4(),
        "scrape_cache_id": SCRAPE_CACHE_ID,
    },
]


def _auth_client(user=None):
    """Return a TestClient with require_current_user overridden."""
    _user = user or make_mock_user()
    app.dependency_overrides[require_current_user] = lambda: _user
    app.state.limiter._disabled = True
    client = TestClient(app)
    return client


def _clear_overrides():
    app.dependency_overrides.clear()


class TestExportCsv:
    def teardown_method(self, method):
        _clear_overrides()

    @patch("app.routers.export.execute", new_callable=AsyncMock)
    @patch("app.routers.export.fetch", new_callable=AsyncMock)
    @patch("app.routers.export.fetchrow", new_callable=AsyncMock)
    def test_export_returns_csv(self, mock_fetchrow, mock_fetch, mock_execute):
        mock_fetchrow.return_value = MOCK_SEARCH
        mock_fetch.return_value = MOCK_RESULTS
        mock_execute.return_value = None

        client = _auth_client()
        resp = client.get(f"/api/export/{SEARCH_ID}")

        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/csv")
        assert f"mapsearch-{SEARCH_ID}" in resp.headers["content-disposition"]

        # Verify CSV structure
        lines = resp.text.strip().split("\n")
        # First line is the header
        header = lines[0]
        assert "business_name" in header
        assert "category" in header
        assert "email" in header
        assert "rating" in header

        # Should have header + 2 data rows
        assert len(lines) == 3

        # Spot-check first data row
        assert "Acme Corp" in lines[1]
        assert "Beta LLC" in lines[2]

    @patch("app.routers.export.fetchrow", new_callable=AsyncMock)
    def test_export_wrong_user_returns_404(self, mock_fetchrow):
        """A search belonging to a different user must return 404, NOT 403."""
        # fetchrow returns None because user_id filter doesn't match
        mock_fetchrow.return_value = None

        client = _auth_client()
        resp = client.get(f"/api/export/{SEARCH_ID}")

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Search not found"

    @patch("app.routers.export.fetchrow", new_callable=AsyncMock)
    def test_export_nonexistent_returns_404(self, mock_fetchrow):
        """A completely unknown search_id must return 404."""
        mock_fetchrow.return_value = None

        client = _auth_client()
        resp = client.get(f"/api/export/{uuid.uuid4()}")

        assert resp.status_code == 404
        assert resp.json()["detail"] == "Search not found"

    def test_export_requires_auth(self):
        """Without authentication, export must return 401."""
        # No dependency override — use real require_current_user
        _clear_overrides()
        # Patch queries.get_user_by_id so auth doesn't hit DB
        with patch("app.routers.auth.queries") as mock_queries:
            mock_queries.get_user_by_id = AsyncMock(return_value=None)
            fresh_client = TestClient(app)
            resp = fresh_client.get(f"/api/export/{SEARCH_ID}")

        assert resp.status_code == 401

    @patch("app.routers.export.execute", new_callable=AsyncMock)
    @patch("app.routers.export.fetch", new_callable=AsyncMock)
    @patch("app.routers.export.fetchrow", new_callable=AsyncMock)
    def test_export_logs_to_exports_table(self, mock_fetchrow, mock_fetch, mock_execute):
        """After a successful export, INSERT INTO exports must be called."""
        mock_fetchrow.return_value = MOCK_SEARCH
        mock_fetch.return_value = MOCK_RESULTS
        mock_execute.return_value = None

        user = make_mock_user()
        client = _auth_client(user)
        resp = client.get(f"/api/export/{SEARCH_ID}")

        assert resp.status_code == 200
        mock_execute.assert_called_once()

        # Verify the INSERT call includes the right positional args
        call_args = mock_execute.call_args
        # call_args.args = (query, user_id, search_id, row_count, filters_applied)
        args = call_args.args
        assert "INSERT INTO exports" in args[0]
        assert args[1] == user["id"]           # user_id
        assert args[2] == SEARCH_ID            # search_id
        assert args[3] == len(MOCK_RESULTS)    # row_count
        assert args[4] is None                 # filters_applied
