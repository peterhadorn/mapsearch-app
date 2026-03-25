"""Async database connection pool for MapSearch using asyncpg."""

import asyncpg
from app.config import DATABASE_URL

_pool = None


async def get_pool():
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    return _pool


async def execute(query, *args):
    pool = await get_pool()
    return await pool.execute(query, *args)


async def fetchrow(query, *args):
    pool = await get_pool()
    return await pool.fetchrow(query, *args)


async def fetch(query, *args):
    pool = await get_pool()
    return await pool.fetch(query, *args)
