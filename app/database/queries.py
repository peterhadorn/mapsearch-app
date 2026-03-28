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
