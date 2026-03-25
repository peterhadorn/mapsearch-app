"""Tests for credit_service — deduct, add, balance functions."""

import uuid
import pytest
from unittest.mock import AsyncMock, call, patch


USER_ID = uuid.uuid4()


# ---------------------------------------------------------------------------
# get_balance
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_balance_returns_credits():
    """fetchrow returns a row with 99 credits — get_balance should return 99."""
    mock_row = {"credits_remaining": 99}
    with patch("app.services.credit_service.fetchrow", new=AsyncMock(return_value=mock_row)):
        from app.services.credit_service import get_balance
        result = await get_balance(USER_ID)
    assert result == 99


@pytest.mark.asyncio
async def test_get_balance_user_not_found():
    """fetchrow returns None — get_balance should raise ValueError."""
    with patch("app.services.credit_service.fetchrow", new=AsyncMock(return_value=None)):
        from app.services.credit_service import get_balance
        with pytest.raises(ValueError, match="User not found"):
            await get_balance(USER_ID)


# ---------------------------------------------------------------------------
# deduct_credits
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_deduct_credits_success():
    """Deduct 10 from balance of 99 — verify UPDATE and INSERT executed correctly."""
    mock_row = {"credits_remaining": 99}
    mock_execute = AsyncMock()

    with patch("app.services.credit_service.fetchrow", new=AsyncMock(return_value=mock_row)), \
         patch("app.services.credit_service.execute", new=mock_execute):
        from app.services.credit_service import deduct_credits
        result = await deduct_credits(USER_ID, 10)

    assert result == 89
    assert mock_execute.call_count == 2

    # First call: UPDATE users
    first_call_args = mock_execute.call_args_list[0][0]
    assert "UPDATE users" in first_call_args[0]
    assert "credits_remaining - $1" in first_call_args[0]
    assert first_call_args[1] == 10
    assert first_call_args[2] == USER_ID

    # Second call: INSERT into credit_transactions
    second_call_args = mock_execute.call_args_list[1][0]
    assert "INSERT INTO credit_transactions" in second_call_args[0]
    assert second_call_args[1] == USER_ID
    assert second_call_args[2] == -10       # negative amount
    assert second_call_args[3] == "search"  # default transaction_type
    assert second_call_args[4] is None      # reference_id default


@pytest.mark.asyncio
async def test_deduct_credits_with_reference_id():
    """Deduct credits with a reference_id — verify it is passed to INSERT."""
    mock_row = {"credits_remaining": 50}
    mock_execute = AsyncMock()
    ref_id = uuid.uuid4()

    with patch("app.services.credit_service.fetchrow", new=AsyncMock(return_value=mock_row)), \
         patch("app.services.credit_service.execute", new=mock_execute):
        from app.services.credit_service import deduct_credits
        result = await deduct_credits(USER_ID, 5, reference_id=ref_id)

    assert result == 45
    insert_args = mock_execute.call_args_list[1][0]
    assert insert_args[4] == ref_id


@pytest.mark.asyncio
async def test_deduct_insufficient_raises():
    """Balance of 5 with deduct of 10 — should raise ValueError."""
    mock_row = {"credits_remaining": 5}

    with patch("app.services.credit_service.fetchrow", new=AsyncMock(return_value=mock_row)):
        from app.services.credit_service import deduct_credits
        with pytest.raises(ValueError, match="Insufficient credits"):
            await deduct_credits(USER_ID, 10)


# ---------------------------------------------------------------------------
# add_credits
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_credits_success():
    """Add 1000 credits — verify UPDATE and INSERT executed, return new balance."""
    mock_execute = AsyncMock()
    # get_balance is called at the end of add_credits
    mock_row_after = {"credits_remaining": 1099}

    with patch("app.services.credit_service.execute", new=mock_execute), \
         patch("app.services.credit_service.fetchrow", new=AsyncMock(return_value=mock_row_after)):
        from app.services.credit_service import add_credits
        result = await add_credits(USER_ID, 1000, stripe_payment_id="pi_test_123")

    assert result == 1099
    assert mock_execute.call_count == 2

    # First call: UPDATE users
    first_call_args = mock_execute.call_args_list[0][0]
    assert "UPDATE users" in first_call_args[0]
    assert "credits_remaining + $1" in first_call_args[0]
    assert first_call_args[1] == 1000
    assert first_call_args[2] == USER_ID

    # Second call: INSERT into credit_transactions
    second_call_args = mock_execute.call_args_list[1][0]
    assert "INSERT INTO credit_transactions" in second_call_args[0]
    assert second_call_args[1] == USER_ID
    assert second_call_args[2] == 1000          # positive amount
    assert second_call_args[3] == "purchase"
    assert second_call_args[4] == "pi_test_123"


@pytest.mark.asyncio
async def test_add_credits_no_stripe_id():
    """add_credits with no stripe_payment_id — stripe_payment_id should be None."""
    mock_execute = AsyncMock()
    mock_row_after = {"credits_remaining": 199}

    with patch("app.services.credit_service.execute", new=mock_execute), \
         patch("app.services.credit_service.fetchrow", new=AsyncMock(return_value=mock_row_after)):
        from app.services.credit_service import add_credits
        result = await add_credits(USER_ID, 100)

    insert_args = mock_execute.call_args_list[1][0]
    assert insert_args[4] is None
