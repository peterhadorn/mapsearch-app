"""Credit management for MapSearch — deduct, add, check balance."""

from app.database.connection import fetchrow, execute


async def get_balance(user_id) -> int:
    """Return current credit balance for user."""
    row = await fetchrow("SELECT credits_remaining FROM users WHERE id = $1", user_id)
    if not row:
        raise ValueError("User not found")
    return row["credits_remaining"]


async def deduct_credits(user_id, amount: int, reference_id=None, transaction_type: str = "search"):
    """Deduct credits and log transaction. Raises if insufficient."""
    balance = await get_balance(user_id)
    if balance < amount:
        raise ValueError(f"Insufficient credits: have {balance}, need {amount}")

    await execute(
        "UPDATE users SET credits_remaining = credits_remaining - $1 WHERE id = $2",
        amount, user_id
    )
    await execute("""
        INSERT INTO credit_transactions (user_id, amount, type, reference_id)
        VALUES ($1, $2, $3, $4)
    """, user_id, -amount, transaction_type, reference_id)

    return balance - amount


async def add_credits(user_id, amount: int, stripe_payment_id: str = None):
    """Add credits from purchase and log transaction."""
    await execute(
        "UPDATE users SET credits_remaining = credits_remaining + $1 WHERE id = $2",
        amount, user_id
    )
    await execute("""
        INSERT INTO credit_transactions (user_id, amount, type, stripe_payment_id)
        VALUES ($1, $2, $3, $4)
    """, user_id, amount, "purchase", stripe_payment_id)

    return await get_balance(user_id)
