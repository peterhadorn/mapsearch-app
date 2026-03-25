"""Async database queries for MapSearch (asyncpg — uses $1, $2 params)."""

from app.database.connection import fetchrow, fetch, execute


async def create_user(email, password_hash, name=None, google_id=None, locale='en'):
    return await fetchrow("""
        INSERT INTO users (email, password_hash, name, google_id, locale)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, email, credits_remaining, locale, created_at
    """, email, password_hash, name, google_id, locale)


async def get_user_by_email(email):
    return await fetchrow("SELECT * FROM users WHERE email = $1", email)


async def get_user_by_id(user_id):
    return await fetchrow("SELECT * FROM users WHERE id = $1", user_id)


async def get_user_by_google_id(google_id):
    return await fetchrow("SELECT * FROM users WHERE google_id = $1", google_id)


async def link_google_id(user_id, google_id):
    return await execute("UPDATE users SET google_id = $1 WHERE id = $2", google_id, user_id)
