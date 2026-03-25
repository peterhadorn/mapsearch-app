"""Tests for the Nominatim geocoder service. Never hits real Nominatim."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.geocoder import geocode

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def nominatim_manhattan():
    """Canned Nominatim response for 'Manhattan, NY'."""
    return json.loads((FIXTURES_DIR / "nominatim_manhattan.json").read_text())


def _make_mock_response(payload):
    """Return a mock httpx.Response whose .json() returns payload."""
    mock_resp = MagicMock()
    mock_resp.json.return_value = payload
    return mock_resp


@pytest.mark.asyncio
async def test_geocode_returns_lat_lng(nominatim_manhattan):
    """geocode() returns correct lat, lng, and country_code for a known location."""
    mock_resp = _make_mock_response(nominatim_manhattan)

    with patch("app.services.geocoder.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await geocode("Manhattan, NY")

    assert result is not None
    assert pytest.approx(result["lat"], abs=0.001) == 40.7830603
    assert pytest.approx(result["lng"], abs=0.001) == -73.9712488
    assert result["country_code"] == "US"
    assert "Manhattan" in result["display_name"]


@pytest.mark.asyncio
async def test_geocode_empty_results_returns_none():
    """geocode() returns None when Nominatim returns an empty list."""
    mock_resp = _make_mock_response([])

    with patch("app.services.geocoder.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await geocode("xyzzy-does-not-exist-12345")

    assert result is None


@pytest.mark.asyncio
async def test_geocode_includes_country_code(nominatim_manhattan):
    """geocode() extracts country_code from the address block and uppercases it."""
    # The fixture has "country_code": "us" (lowercase) — verify it comes back as "US"
    mock_resp = _make_mock_response(nominatim_manhattan)

    with patch("app.services.geocoder.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await geocode("Manhattan, NY")

    assert result is not None
    assert result["country_code"] == "US"
    assert result["country_code"] == result["country_code"].upper()
