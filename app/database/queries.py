"""Async database queries for MapSearch (asyncpg — uses $1, $2 params)."""

from app.database.connection import fetchrow, fetch, execute


async def create_user(email, password_hash, name=None, locale='en'):
    return await fetchrow("""
        INSERT INTO users (email, password_hash, name, locale)
        VALUES ($1, $2, $3, $4)
        RETURNING id, email, credits_remaining, locale, created_at
    """, email, password_hash, name, locale)


async def get_user_by_email(email):
    return await fetchrow(
        "SELECT * FROM users WHERE email = $1 AND deleted_at IS NULL", email
    )


async def get_user_by_id(user_id):
    return await fetchrow(
        "SELECT * FROM users WHERE id = $1 AND deleted_at IS NULL", user_id
    )


async def create_reset_token(user_id, token_hash, expires_at):
    return await execute("""
        INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
        VALUES ($1, $2, $3)
    """, user_id, token_hash, expires_at)


async def get_valid_reset_token(token_hash):
    return await fetchrow("""
        SELECT * FROM password_reset_tokens
        WHERE token_hash = $1
        AND expires_at > NOW()
        AND used_at IS NULL
    """, token_hash)


async def mark_token_used(token_id):
    return await execute(
        "UPDATE password_reset_tokens SET used_at = NOW() WHERE id = $1",
        token_id
    )


async def update_user_password(user_id, password_hash):
    return await execute(
        "UPDATE users SET password_hash = $1 WHERE id = $2",
        password_hash, user_id
    )


async def soft_delete_user(user_id):
    return await execute(
        "UPDATE users SET deleted_at = NOW() WHERE id = $1",
        user_id
    )


async def purge_deleted_users():
    """Permanently delete users whose deleted_at is older than 30 days."""
    return await execute("""
        DELETE FROM users
        WHERE deleted_at IS NOT NULL
        AND deleted_at < NOW() - INTERVAL '30 days'
    """)


async def get_credit_transactions(user_id, limit=50, offset=0):
    return await fetch("""
        SELECT id, amount, type, reference_id, stripe_payment_id, created_at
        FROM credit_transactions
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
    """, user_id, limit, offset)


async def count_credit_transactions(user_id):
    row = await fetchrow(
        "SELECT COUNT(*) as total FROM credit_transactions WHERE user_id = $1",
        user_id
    )
    return row["total"]


async def get_user_searches(user_id, limit=50, offset=0):
    return await fetch("""
        SELECT s.id, s.filters_applied, s.filtered_result_count, s.credits_used, s.created_at,
               sc.keyword, sc.location
        FROM searches s
        JOIN scrape_cache sc ON s.scrape_cache_id = sc.id
        WHERE s.user_id = $1
        ORDER BY s.created_at DESC
        LIMIT $2 OFFSET $3
    """, user_id, limit, offset)


async def count_user_searches(user_id):
    row = await fetchrow(
        "SELECT COUNT(*) as total FROM searches WHERE user_id = $1",
        user_id
    )
    return row["total"]


async def get_search_with_results(search_id, user_id):
    """Get a single search and its filtered results via the junction table."""
    search = await fetchrow("""
        SELECT s.id, s.filters_applied, s.filtered_result_count, s.credits_used, s.created_at,
               sc.keyword, sc.location, sc.latitude, sc.longitude, sc.zoom_level
        FROM searches s
        JOIN scrape_cache sc ON s.scrape_cache_id = sc.id
        WHERE s.id = $1 AND s.user_id = $2
    """, search_id, user_id)
    if not search:
        return None, None

    results = await fetch("""
        SELECT sr.* FROM search_results sr
        JOIN search_result_ids sri ON sr.id = sri.search_result_id
        WHERE sri.search_id = $1
    """, search_id)
    return search, results


# --- Admin queries ---

async def admin_get_stats():
    """Get system-wide stats for admin dashboard."""
    users = await fetchrow("SELECT COUNT(*) as total FROM users WHERE deleted_at IS NULL")
    searches = await fetchrow("SELECT COUNT(*) as total FROM searches")
    credits_sold = await fetchrow(
        "SELECT COALESCE(SUM(amount), 0) as total FROM credit_transactions WHERE type = 'purchase'"
    )
    total_credits = credits_sold["total"]
    estimated_revenue = round(total_credits * 1.40 / 1000, 2)
    return {
        "total_users": users["total"],
        "total_searches": searches["total"],
        "total_credits_sold": total_credits,
        "estimated_revenue": estimated_revenue,
    }


async def admin_get_users(limit=50, offset=0):
    return await fetch("""
        SELECT u.id, u.email, u.credits_remaining, u.created_at, u.last_login_at, u.deleted_at,
               COUNT(s.id) as search_count
        FROM users u
        LEFT JOIN searches s ON s.user_id = u.id
        GROUP BY u.id
        ORDER BY u.created_at DESC
        LIMIT $1 OFFSET $2
    """, limit, offset)


async def admin_count_users():
    row = await fetchrow("SELECT COUNT(*) as total FROM users")
    return row["total"]


async def admin_get_searches(limit=50, offset=0):
    return await fetch("""
        SELECT s.id, s.filtered_result_count, s.credits_used, s.created_at,
               sc.keyword, sc.location,
               u.email as user_email
        FROM searches s
        JOIN scrape_cache sc ON s.scrape_cache_id = sc.id
        JOIN users u ON s.user_id = u.id
        ORDER BY s.created_at DESC
        LIMIT $1 OFFSET $2
    """, limit, offset)


async def admin_count_searches():
    row = await fetchrow("SELECT COUNT(*) as total FROM searches")
    return row["total"]


async def admin_get_revenue(limit=50, offset=0):
    return await fetch("""
        SELECT ct.amount, ct.stripe_payment_id, ct.created_at,
               u.email as user_email
        FROM credit_transactions ct
        JOIN users u ON ct.user_id = u.id
        WHERE ct.type = 'purchase'
        ORDER BY ct.created_at DESC
        LIMIT $1 OFFSET $2
    """, limit, offset)


async def admin_count_revenue():
    row = await fetchrow("SELECT COUNT(*) as total FROM credit_transactions WHERE type = 'purchase'")
    return row["total"]


async def admin_adjust_credits(user_id, amount):
    """Add or subtract credits. Amount can be negative."""
    await execute(
        "UPDATE users SET credits_remaining = credits_remaining + $1 WHERE id = $2",
        amount, user_id
    )
    await execute("""
        INSERT INTO credit_transactions (user_id, amount, type)
        VALUES ($1, $2, $3)
    """, user_id, amount, "admin_adjustment")


async def admin_delete_user(user_id):
    """Soft delete a user (sets deleted_at, consistent with existing architecture)."""
    await execute("UPDATE users SET deleted_at = NOW() WHERE id = $1", user_id)
