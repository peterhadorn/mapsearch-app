# MapSearch.app MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the MapSearch.app MVP — a web app where users search Google Maps business data by keyword + location, filter on 10+ fields, view results in a live table with map pins, and export as CSV. Pay-per-result credits via Stripe.

**Architecture:** Standalone FastAPI app in `projects/mapsearch/` with NEW async DataForSEO client (live/sync endpoint for instant results). Vanilla JS + Leaflet.js frontend with pub/sub state management. PostgreSQL via asyncpg. Deployed on existing VPS behind Caddy.

**Tech Stack:** FastAPI, Jinja2, vanilla JS, Leaflet.js, DataForSEO Live API (`/v3/serp/google/maps/live/advanced`), PostgreSQL (asyncpg), Stripe Checkout, Google OAuth2, Caddy, Nominatim (geocoding)

**API Cost Note:** Using DataForSEO live/sync endpoint at $0.002/SERP (not async at $0.0006). Required for "results in seconds" UX promise. At $1.50/1000 credits to users, margin remains >80%.

**Deferred to v1.1:** Search history page, saved searches, email templates (welcome/receipt), responsive mobile layout, Pingen integration

**Design Reference:** `projects/mapsearch/design/` — CSS design system, component library, app.html prototype, i18n JSON files

**Master Plan:** `plans/explorations/2026-03-24-MAPSEARCH-SAAS.md`

---

## File Structure

```
projects/mapsearch/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app, middleware, CORS
│   ├── config.py                  # Settings, env vars, constants
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py                # Google OAuth + email/password signup/login
│   │   ├── search.py              # Search endpoint (DataForSEO)
│   │   ├── export.py              # CSV export
│   │   ├── credits.py             # Credit balance, purchase, Stripe webhook
│   │   └── pages.py               # HTML page routes (landing, history)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── search_service.py      # DataForSEO call, caching, credit deduction
│   │   ├── dataforseo_client.py   # NEW async DataForSEO live API client (not shared scraper)
│   │   ├── geocoder.py            # Location name → lat/lng (Nominatim)
│   │   ├── location_resolver.py   # Country → DataForSEO location_code mapping
│   │   └── credit_service.py      # Credit math, transactions
│   ├── database/
│   │   ├── __init__.py
│   │   ├── schema.sql             # Full DDL
│   │   ├── queries.py             # All SQL queries
│   │   └── connection.py          # asyncpg connection pool
│   ├── models/
│   │   ├── __init__.py
│   │   └── request_models.py      # Pydantic models for all API inputs
│   ├── templates/
│   │   ├── base.html              # Jinja2 base layout
│   │   ├── app.html               # Main product page
│   │   └── partials/
│   │       ├── header.html
│   │       ├── search_card.html
│   │       ├── results_table.html
│   │       └── signup_modal.html
│   ├── static/
│   │   ├── css/
│   │   │   ├── design-system.css  # Copy from design/
│   │   │   ├── layout.css         # Copy from design/
│   │   │   └── components.css     # Copy from design/
│   │   ├── js/
│   │   │   ├── state.js           # Pub/sub event bus + global state
│   │   │   ├── app.js             # Main app logic, orchestrates modules
│   │   │   ├── map.js             # Leaflet map, pins, interactions
│   │   │   ├── table.js           # Table sorting, filtering, rendering
│   │   │   ├── filters.js         # Filter controls
│   │   │   ├── auth.js            # Signup/login modal logic
│   │   │   ├── credits.js         # Credit display, purchase flow
│   │   │   ├── i18n.js            # Translation loader
│   │   │   └── theme.js           # Light/dark/system toggle
│   │   └── i18n/
│   │       ├── en.json
│   │       ├── fr.json
│   │       ├── es.json
│   │       └── de.json
│   └── .env.example               # All required env vars documented
├── tests/
│   ├── conftest.py                # Test DB, test client, auth fixtures, DataForSEO mock
│   ├── fixtures/
│   │   └── dataforseo_response.json  # Canned DataForSEO response (never hit real API in tests)
│   ├── test_search_service.py
│   ├── test_credit_service.py
│   ├── test_geocoder.py
│   ├── test_auth.py
│   └── test_export.py
├── requirements.txt
└── README.md
```

---

## Task Ordering (Fixed per review)

**Dependency fixes applied:**
- Credit Service moved BEFORE Search Service (search needs credits)
- Auth Modal moved BEFORE Search Flow (search triggers modal)
- State module added as Task 0 in frontend phase
- DataForSEO location resolver added as new task
- DataForSEO async client added as new task (NOT reusing shared sync scraper)

**Parallelizable groups:**
- Tasks 4+5 (Auth) || Task 6 (Geocoder) || Task 6b (Location Resolver) — all only need DB
- Tasks 10, 11, 12 (Map, Filters, Table) — independent frontend modules
- Task 16 (Stripe) || Task 14 (i18n) — no dependencies on each other

---

## Phase 1: Scaffolding + Database (Tasks 1-3)

### Task 1: Project Scaffolding

**Files:**
- Create: `projects/mapsearch/app/__init__.py`
- Create: `projects/mapsearch/app/main.py`
- Create: `projects/mapsearch/app/config.py`
- Create: `projects/mapsearch/requirements.txt`
- Create: `projects/mapsearch/app/routers/__init__.py`
- Create: `projects/mapsearch/app/services/__init__.py`
- Create: `projects/mapsearch/app/database/__init__.py`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p projects/mapsearch/app/{routers,services,database,templates/partials,static/{css,js,i18n}}
mkdir -p projects/mapsearch/tests
```

- [ ] **Step 2: Create requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
asyncpg==0.29.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.27.0
stripe==8.0.0
python-multipart==0.0.9
jinja2==3.1.4
slowapi==0.1.9
pydantic[email]==2.9.0
pytest-asyncio==0.24.0
```

- [ ] **Step 3: Create config.py**

```python
"""MapSearch configuration — all settings from environment variables."""

import os

DATAFORSEO_LOGIN = os.environ["DATAFORSEO_LOGIN"]
DATAFORSEO_PASSWORD = os.environ["DATAFORSEO_PASSWORD"]
DATABASE_URL = os.environ["MAPSEARCH_DATABASE_URL"]
STRIPE_SECRET_KEY = os.environ["STRIPE_SECRET_KEY"]
STRIPE_WEBHOOK_SECRET = os.environ["STRIPE_WEBHOOK_SECRET"]
GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
SECRET_KEY = os.environ["MAPSEARCH_SECRET_KEY"]

SIGNUP_BONUS_CREDITS = 99
CACHE_DURATION_HOURS = 72
DATAFORSEO_MAX_DEPTH = 700

# DataForSEO zoom levels → user-facing labels
ZOOM_LEVELS = {
    14: {"label": "Neighborhood", "miles": "~3 mi", "km": "~5 km"},
    13: {"label": "District", "miles": "~6 mi", "km": "~10 km"},
    12: {"label": "City", "miles": "~12 mi", "km": "~20 km"},
    11: {"label": "Metro", "miles": "~25 mi", "km": "~40 km"},
}

# JWT config — httpOnly cookies, NOT localStorage (XSS prevention)
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 168  # 7 days
JWT_COOKIE_NAME = "mapsearch_session"
```

- [ ] **Step 4: Create main.py (minimal FastAPI app)**

```python
"""MapSearch.app — main FastAPI application."""

import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger("mapsearch")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="MapSearch", docs_url=None, redoc_url=None)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(CORSMiddleware, allow_origins=["https://mapsearch.app"], allow_methods=["*"], allow_headers=["*"])

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
```

- [ ] **Step 5: Verify it starts**

```bash
cd projects/mapsearch && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8100
```
Expected: Server starts on port 8100

- [ ] **Step 6: Commit**

```bash
git add projects/mapsearch/
git commit -m "feat(mapsearch): project scaffolding"
```

---

### Task 2: Database Schema

**Files:**
- Create: `projects/mapsearch/app/database/schema.sql`
- Create: `projects/mapsearch/app/database/connection.py`

- [ ] **Step 1: Write schema.sql**

```sql
-- MapSearch.app database schema

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    name VARCHAR(255),
    google_id VARCHAR(255) UNIQUE,
    credits_remaining INTEGER DEFAULT 99,
    locale VARCHAR(5) DEFAULT 'en',
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);

-- Raw scrape cache — stores UNFILTERED DataForSEO results.
-- Cache key is keyword+location+zoom+near_me only (filters are NOT part of cache key).
-- Different filter sets reuse the same cached raw data — filters are applied post-cache.
CREATE TABLE scrape_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    zoom_level INTEGER DEFAULT 13,
    near_me BOOLEAN DEFAULT FALSE,
    country VARCHAR(10),
    raw_result_count INTEGER,
    cache_key VARCHAR(500) GENERATED ALWAYS AS (
        lower(trim(keyword)) || '|' || lower(trim(location)) || '|' || zoom_level || '|' || near_me || '|' || lower(coalesce(country, ''))
    ) STORED,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_cache_key ON scrape_cache(cache_key, created_at DESC);

-- User searches — records each search a user makes WITH their filters.
-- Links to scrape_cache for the raw data, stores filtered result count + credits charged.
CREATE TABLE searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    scrape_cache_id UUID REFERENCES scrape_cache(id),
    filters_applied JSONB NOT NULL DEFAULT '{}',
    filtered_result_count INTEGER,
    credits_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_searches_user ON searches(user_id, created_at DESC);

-- Raw results linked to scrape_cache (not to individual user searches).
-- Multiple users can share the same cached results with different filters.
CREATE TABLE search_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scrape_cache_id UUID REFERENCES scrape_cache(id) ON DELETE CASCADE,
    business_name VARCHAR(500),
    domain VARCHAR(500),
    url TEXT,
    phone VARCHAR(100),
    email VARCHAR(255),
    address TEXT,
    city VARCHAR(255),
    state VARCHAR(100),
    zip VARCHAR(50),
    country VARCHAR(10),
    rating NUMERIC(2,1),
    reviews_count INTEGER,
    place_id VARCHAR(255),
    cid VARCHAR(255),
    google_maps_url TEXT,
    category VARCHAR(255),
    additional_categories JSONB,
    category_ids JSONB,
    is_claimed BOOLEAN,
    verified BOOLEAN,
    photos_count INTEGER,
    main_image TEXT,
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    price_level VARCHAR(10),
    work_hours JSONB,
    business_status VARCHAR(50),
    rating_distribution JSONB,
    has_website BOOLEAN GENERATED ALWAYS AS (domain IS NOT NULL AND domain != '') STORED,
    has_email BOOLEAN GENERATED ALWAYS AS (email IS NOT NULL AND email != '') STORED,
    has_phone BOOLEAN GENERATED ALWAYS AS (phone IS NOT NULL AND phone != '') STORED
);
CREATE INDEX idx_results_cache ON search_results(scrape_cache_id);
CREATE INDEX idx_results_filters ON search_results(has_website, has_email, rating, reviews_count);

CREATE TABLE credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    amount INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL,
    reference_id UUID,
    stripe_payment_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
CREATE INDEX idx_credits_user ON credit_transactions(user_id, created_at DESC);

CREATE TABLE exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    search_id UUID REFERENCES searches(id),
    row_count INTEGER,
    filters_applied JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

- [ ] **Step 2: Write connection.py**

```python
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
```

**Note:** asyncpg uses `$1, $2` parameter placeholders (not `%s`). All queries must use PostgreSQL native params.

- [ ] **Step 3: Create database + user on VPS**

```bash
ssh root@82.21.4.94 "sudo -u postgres psql -c \"CREATE USER mapsearch WITH PASSWORD 'GENERATE_SECURE_PASSWORD';\""
ssh root@82.21.4.94 "sudo -u postgres psql -c \"CREATE DATABASE mapsearch OWNER mapsearch;\""
ssh root@82.21.4.94 "sudo -u postgres psql mapsearch < /dev/stdin" < projects/mapsearch/app/database/schema.sql
ssh root@82.21.4.94 "sudo -u postgres psql -c \"GRANT ALL ON ALL TABLES IN SCHEMA public TO mapsearch;\" mapsearch"
```

- [ ] **Step 4: Commit**

```bash
git add projects/mapsearch/app/database/
git commit -m "feat(mapsearch): database schema + connection pool"
```

---

### Task 3: Copy Design Assets

**Files:**
- Copy: `projects/mapsearch/design/css/*.css` → `projects/mapsearch/app/static/css/`
- Copy: `projects/mapsearch/design/i18n/*.json` → `projects/mapsearch/app/static/i18n/`

- [ ] **Step 1: Copy CSS files**

```bash
cp projects/mapsearch/design/css/design-system.css projects/mapsearch/app/static/css/
cp projects/mapsearch/design/css/layout.css projects/mapsearch/app/static/css/
cp projects/mapsearch/design/css/components.css projects/mapsearch/app/static/css/
```

- [ ] **Step 2: Copy i18n files**

```bash
cp projects/mapsearch/design/i18n/*.json projects/mapsearch/app/static/i18n/
```

- [ ] **Step 3: Commit**

```bash
git add projects/mapsearch/app/static/
git commit -m "feat(mapsearch): copy design assets to app static"
```

---

## Phase 2: Auth (Tasks 4-5)

### Task 4: Email/Password Auth

**Files:**
- Create: `projects/mapsearch/app/routers/auth.py`
- Create: `projects/mapsearch/app/database/queries.py`
- Create: `projects/mapsearch/tests/test_auth.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_auth.py
def test_signup_creates_user_with_99_credits():
    """New user gets 99 signup bonus credits."""
    # POST /api/auth/signup with email + password
    # Assert 201, user created, credits_remaining = 99
    pass

def test_signup_duplicate_email_returns_409():
    pass

def test_login_returns_session_token():
    pass

def test_login_wrong_password_returns_401():
    pass
```

- [ ] **Step 2: Write queries.py (user CRUD)**

```python
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
```

- [ ] **Step 3: Write auth.py router**

Endpoints:
- `POST /api/auth/signup` — email + password → create user, set JWT in httpOnly cookie
- `POST /api/auth/login` — email + password → verify, set JWT in httpOnly cookie
- `POST /api/auth/logout` — clear JWT cookie
- `GET /api/auth/me` — return current user from JWT cookie

Use `python-jose` for JWT, `passlib[bcrypt]` for password hashing.

**Security:** JWT stored as httpOnly, Secure, SameSite=Lax cookie (NOT localStorage — XSS prevention). All state-mutating endpoints validate JWT from cookie. Rate limit: 5 signups/minute per IP, 10 logins/minute per IP.

**Pydantic models** (in `models/request_models.py`):
```python
from pydantic import BaseModel, EmailStr

class SignupRequest(BaseModel):
    email: EmailStr
    password: str  # min 8 chars validated in endpoint

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
```

- [ ] **Step 4: Run tests, verify pass**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(mapsearch): email/password auth + JWT sessions"
```

---

### Task 5: Google OAuth

**Files:**
- Modify: `projects/mapsearch/app/routers/auth.py`

- [ ] **Step 1: Add Google OAuth endpoints**

- `GET /api/auth/google` — generate `state` param (random token, store in session/cookie), redirect to Google OAuth consent screen with state
- `GET /api/auth/google/callback` — **validate state param matches** (CSRF prevention for OAuth), exchange code for tokens, verify ID token, extract email + name + google_id

Use `httpx` to exchange code for tokens, verify ID token, extract email + name + google_id.

If user exists (by google_id or email) → login. If new → create with 99 credits.

**OAuth security:**
- `state` parameter is mandatory — generate random token, store in httpOnly cookie, validate on callback. Without this, OAuth is vulnerable to CSRF login attacks.
- Verify `id_token` signature using Google's JWKS endpoint, check `aud` matches our client_id.

**CSRF protection for all mutating endpoints:**
- SameSite=Lax cookies prevent cross-origin form submissions
- Additionally, all POST/PUT/DELETE endpoints must check `Origin` or `Referer` header matches `mapsearch.app`. Reject requests from other origins.
- This is simpler than CSRF tokens and works with cookie-based auth.

- [ ] **Step 2: Test with real Google OAuth (manual)**

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(mapsearch): Google OAuth2 signup/login"
```

---

## Phase 3: Core Search (Tasks 6-8b)

### Task 6b: DataForSEO Location Resolver

**Files:**
- Create: `projects/mapsearch/app/services/location_resolver.py`

- [ ] **Step 1: Build country → location_code mapping**

DataForSEO has a free endpoint: `GET /v3/serp/google/locations/{country}`. Use it to build a lookup.

For MVP, hardcode the top 20 countries:

```python
"""Map country codes to DataForSEO location_codes."""

# Top 20 countries — extend from DataForSEO /v3/serp/google/locations/ (free endpoint)
LOCATION_CODES = {
    "US": 2840, "GB": 2826, "DE": 2276, "FR": 2250, "CH": 2756,
    "AT": 2040, "IT": 2380, "ES": 2724, "NL": 2528, "BE": 2056,
    "CA": 2124, "AU": 2036, "BR": 2076, "MX": 2484, "IN": 2356,
    "JP": 2392, "KR": 2410, "SE": 2752, "NO": 2578, "DK": 2208,
}

# Language codes per country
LANGUAGE_CODES = {
    "US": "en", "GB": "en", "DE": "de", "FR": "fr", "CH": "de",
    "AT": "de", "IT": "it", "ES": "es", "NL": "nl", "BE": "fr",
    "CA": "en", "AU": "en", "BR": "pt", "MX": "es", "IN": "en",
    "JP": "ja", "KR": "ko", "SE": "sv", "NO": "no", "DK": "da",
}


def resolve_location(country_code: str) -> dict:
    """Return DataForSEO location_code and language_code for a country."""
    code = country_code.upper()
    return {
        "location_code": LOCATION_CODES.get(code, 2840),  # Default US
        "language_code": LANGUAGE_CODES.get(code, "en"),
    }
```

- [ ] **Step 2: Integrate with geocoder**

After geocoding a location name, reverse-geocode the country from the coordinates (Nominatim returns country_code in results). Pass to location_resolver.

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(mapsearch): DataForSEO location resolver — country to location_code"
```

---

### Task 6: Geocoder Service

**Files:**
- Create: `projects/mapsearch/app/services/geocoder.py`
- Create: `projects/mapsearch/tests/test_geocoder.py`

- [ ] **Step 1: Write failing test**

```python
# All geocoder tests use mocked httpx responses — NEVER hit real Nominatim.
# Store canned responses in tests/fixtures/nominatim_manhattan.json

@pytest.fixture
def mock_nominatim(monkeypatch):
    """Mock Nominatim API response."""
    async def mock_get(*args, **kwargs):
        return MockResponse([{"lat": "40.7831", "lon": "-73.9712", "display_name": "Manhattan, NY, USA"}])
    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)

@pytest.mark.asyncio
async def test_geocode_manhattan(mock_nominatim):
    result = await geocode("Manhattan, NY")
    assert abs(result["lat"] - 40.7831) < 0.05
    assert abs(result["lng"] - (-73.9712)) < 0.05
```

- [ ] **Step 2: Implement geocoder using Nominatim**

```python
"""Geocode location names to coordinates + country code using Nominatim."""

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


async def geocode(location: str) -> dict | None:
    """Convert location name to lat/lng + country_code.

    Returns: {"lat": float, "lng": float, "country_code": str, "display_name": str} or None
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(NOMINATIM_URL, params={
            "q": location,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,  # Required to get country_code
        }, headers={"User-Agent": "MapSearch.app/1.0"})
        results = resp.json()
        if not results:
            return None
        r = results[0]
        return {
            "lat": float(r["lat"]),
            "lng": float(r["lon"]),
            "country_code": r.get("address", {}).get("country_code", "us").upper(),
            "display_name": r["display_name"],
        }
```

**Key:** `addressdetails=1` makes Nominatim return the `address` object which includes `country_code` (ISO 3166-1 alpha-2, lowercase). This is what `location_resolver.py` needs to map to DataForSEO `location_code`.

- [ ] **Step 3: Run tests**

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(mapsearch): Nominatim geocoder service"
```

---

### Task 7: Search Service (DataForSEO Integration)

**Files:**
- Create: `projects/mapsearch/app/services/search_service.py`
- Create: `projects/mapsearch/tests/test_search_service.py`

This is the core service. It:
1. Checks cache (same keyword+location+zoom = reuse results within 72h)
2. Geocodes location → lat/lng
3. Calls DataForSEO Google Maps API
4. Stores results in DB
5. Deducts credits from user
6. Returns results

- [ ] **Step 1: Write failing test**

```python
def test_search_deducts_credits():
    """Search that returns N results deducts N credits."""
    pass

def test_search_cache_hit_no_credits():
    """Cached search (within 72h) returns results without deducting credits."""
    pass

def test_search_insufficient_credits():
    """Search with 0 credits raises InsufficientCreditsError."""
    pass
```

- [ ] **Step 2: Implement search_service.py**

**IMPORTANT:** Do NOT reuse `shared/scrapers/scrape_dataforseo.py` — it's synchronous (requests.Session) and hardcodes Swiss location_code. Build a NEW async client.

Create `services/dataforseo_client.py`:

```python
"""Async DataForSEO Google Maps Live API client."""

import httpx
from app.config import DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD, DATAFORSEO_MAX_DEPTH

LIVE_ENDPOINT = "https://api.dataforseo.com/v3/serp/google/maps/live/advanced"

async def search_maps(keyword, lat, lng, zoom, location_code, language_code, near_me=False):
    """Search Google Maps via DataForSEO live/sync API. Returns results in seconds."""
    payload = [{
        "keyword": f"{keyword} near me" if near_me else keyword,
        "location_coordinate": f"{lat},{lng},{zoom}",
        "location_code": location_code,
        "language_code": language_code,
        "depth": DATAFORSEO_MAX_DEPTH,
        "device": "desktop",
    }]
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            LIVE_ENDPOINT, json=payload,
            auth=(DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD),
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()
```

Key logic in `search_service.py`:

```
1. Geocode location → lat/lng + country_code
2. Resolve country → DataForSEO location_code + language_code
3. Build cache_key from keyword+location+zoom+near_me
4. Check scrape_cache (same cache_key within 72h?)
   ├── CACHE HIT: load raw results from search_results table
   └── CACHE MISS: call DataForSEO API, store raw results + scrape_cache row
5. Apply filters to raw results → filtered_results
6. filtered_count = len(filtered_results)
7. Check user credits >= filtered_count
   ├── INSUFFICIENT: return error with filtered_count so UI can show
   │   "This search returns ~234 results. You have 10 credits. Buy more?"
   └── SUFFICIENT: proceed
8. Deduct credits = filtered_count (atomic DB transaction)
9. Create searches row (user_id, scrape_cache_id, filters, filtered_count, credits_used)
10. Return filtered_results + metadata
```

**Key design decisions:**
- **Cache stores RAW unfiltered data.** Filters are applied post-cache. Different users with different filters reuse the same cached scrape. We eat the DataForSEO cost once, not per filter combination.
- **Credits = filtered result count.** Filters save the user money. "Has email = Yes" might reduce 618→234, user pays 234.
- **Credit check happens AFTER filtering, BEFORE delivering results.** User never sees data they haven't paid for. If insufficient credits, they see the count but not the data.
- **DataForSEO cost is decoupled from credit charge.** We may pay $0.20 for a 618-result scrape but only charge 234 credits if filters reduce the set. The margin absorbs this — DataForSEO is so cheap it doesn't matter.
- **Cost exposure mitigation for free/throwaway accounts:** Cache is the primary defense. A throwaway account's search populates the cache, so subsequent users (paying ones) get the data for free. The max cost per free account is 1 uncached scrape = ~$0.20. With 99 free credits and typical filter ratios, most free users trigger 1-2 scrapes max. If abuse is detected (many accounts from same IP, all burning free credits on unique uncached searches), rate limit by IP: max 3 searches/hour for unauthenticated IPs. This is a business-acceptable risk at $0.20/abuse-account.
- **Credit deduction is atomic:** single DB transaction for deducting credits + inserting credit_transaction. If transaction fails, neither happens.

- [ ] **Step 3: Implement cache check**

```python
async def find_cached_scrape(cache_key, max_age_hours=72):
    """Find a cached raw scrape within the max age window."""
    return await fetchrow("""
        SELECT id, raw_result_count FROM scrape_cache
        WHERE cache_key = $1
        AND created_at > NOW() - make_interval(hours := $2)
        ORDER BY created_at DESC LIMIT 1
    """, cache_key, max_age_hours)
```

**Note:** Queries `scrape_cache` (raw data), NOT `searches` (user-specific). Uses `make_interval()` for asyncpg param binding.

- [ ] **Step 4: Run tests**

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(mapsearch): search service with DataForSEO + caching + credit deduction"
```

---

### Task 8: Search API Endpoint

**Files:**
- Create: `projects/mapsearch/app/routers/search.py`

- [ ] **Step 1: Implement search endpoint**

```
POST /api/search
Body: {
    "keyword": "Dentist",
    "location": "Manhattan, NY",
    "zoom_level": 13,
    "near_me": false,
    "filters": {
        "has_website": "any",
        "has_email": "any",
        "has_phone": "any",
        "min_rating": 1.0,
        "min_reviews": 0,
        "is_claimed": "any",
        "category": null,
        "price_level": null,
        "has_photos": "any"
    }
}
Response: {
    "search_id": "uuid",
    "result_count": 618,
    "credits_used": 618,
    "credits_remaining": 481,
    "max_reached": false,
    "results": [ ... ]
}
```

If `result_count == 700`: `max_reached: true` — UI shows "Results capped at 700. Try a smaller search area."

**Pydantic request model:**
```python
class SearchRequest(BaseModel):
    keyword: str  # max 255 chars
    location: str  # max 255 chars
    zoom_level: int = 13  # Must be 11, 12, 13, or 14
    near_me: bool = False
    filters: dict = {}
```

**Rate limit:** 10 searches/minute per user.
```

Requires authenticated user (JWT in httpOnly cookie — consistent with auth system).

- [ ] **Step 2: Apply pre-search filters**

Some filters can reduce DataForSEO results (category). Others are post-search (applied to returned data before storing). Document which is which.

- [ ] **Step 3: Test endpoint manually with curl**

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(mapsearch): POST /api/search endpoint"
```

---

## Phase 4: Frontend (Tasks 9-14, 19)

**Note:** Task 19 (Auth Modal) moved here from Phase 6 — search flow depends on it.

### Task 9a: State Management Module

**Files:**
- Create: `projects/mapsearch/app/static/js/state.js`

- [ ] **Step 1: Create pub/sub event bus + global state**

```javascript
/**
 * Minimal pub/sub state management for MapSearch.
 * All modules subscribe to state changes instead of cross-referencing each other.
 */
const State = {
    _state: {
        user: null,           // { id, email, credits }
        searchResults: null,  // array of business objects
        searchMeta: null,     // { search_id, result_count, max_reached }
        filters: {},          // current filter state
        loading: false,
        error: null,
    },
    _listeners: {},

    get(key) { return this._state[key]; },

    set(key, value) {
        this._state[key] = value;
        (this._listeners[key] || []).forEach(fn => fn(value));
    },

    on(key, fn) {
        if (!this._listeners[key]) this._listeners[key] = [];
        this._listeners[key].push(fn);
    },
};
```

All other JS modules (`map.js`, `table.js`, `filters.js`, `auth.js`, `credits.js`) listen to State changes. No direct cross-module calls.

- [ ] **Step 2: Commit**

```bash
git commit -m "feat(mapsearch): state.js — pub/sub event bus for frontend"
```

---

### Task 9b: Auth Modal (moved from Task 19)

**Files:**
- Create: `projects/mapsearch/app/static/js/auth.js`

- [ ] **Step 1: Signup modal HTML** in app.html template

Google OAuth button (prominent) + email/password form. "99 free credits" headline.

- [ ] **Step 2: Wire Google OAuth button**

Click → redirect to `/api/auth/google`.

- [ ] **Step 3: Wire email/password form**

Submit → POST `/api/auth/signup` → JWT set as httpOnly cookie → close modal → State.set('user', data) → execute pending search.

- [ ] **Step 4: Login form toggle**

"Already have an account? Log in" switches form.

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(mapsearch): auth modal — signup/login with Google OAuth + email"
```

---

### Task 9c: Base Template + Landing Page

**Files:**
- Create: `projects/mapsearch/app/templates/base.html`
- Create: `projects/mapsearch/app/templates/app.html`
- Create: `projects/mapsearch/app/routers/pages.py`
- Create: `projects/mapsearch/app/static/js/theme.js`

- [ ] **Step 1: Create base.html (Jinja2 layout)**

Includes: Leaflet CDN, design-system.css, layout.css, components.css, Inter font, theme flash prevention script.

- [ ] **Step 2: Create app.html template**

Port from `projects/mapsearch/design/html/app.html` into Jinja2 template. Replace hardcoded data with template variables. Keep all CSS inline for now (can extract later).

- [ ] **Step 3: Create pages.py router**

```python
@router.get("/")
async def landing(request: Request):
    return templates.TemplateResponse("app.html", {"request": request})
```

- [ ] **Step 4: Create theme.js (light/dark/system toggle)**

Port from the design prototype's theme toggle JS.

- [ ] **Step 5: Verify page loads at localhost:8100**

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(mapsearch): landing page template + theme toggle"
```

---

### Task 10: Map Module

**Files:**
- Create: `projects/mapsearch/app/static/js/map.js`

- [ ] **Step 1: Initialize Leaflet map**

Full-screen, CartoDB Dark Matter tiles, centered on user's location (or NYC default). Map overlay gradient div.

- [ ] **Step 2: Pin rendering**

Function `renderPins(results)` — takes search results array, places colored pins. Click pin → popup (business name, category, rating).

- [ ] **Step 3: Table ↔ Map interaction**

Hover table row → highlight pin (glow/pulse). Click pin → highlight table row. Click table row → pan map to pin.

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(mapsearch): Leaflet map with pins + table interaction"
```

---

### Task 11: Filter Controls

**Files:**
- Create: `projects/mapsearch/app/static/js/filters.js`

- [ ] **Step 1: Implement tri-toggle logic**

Click Yes/No/Any → update state, change CSS classes. Three-way toggles for: has_website, has_email, has_phone, claimed, has_photos.

- [ ] **Step 2: Range sliders**

Rating slider (1-5, step 0.5). Reviews slider (0-500, step 10). Update displayed value on change.

- [ ] **Step 3: Search area toggle**

4-way toggle for zoom level (Neighborhood/District/City/Metro).

- [ ] **Step 4: Near me toggle**

Toggle switch that sets `near_me` flag.

- [ ] **Step 5: Category dropdown + Price level toggle**

- [ ] **Step 6: Collect all filter state into object**

```javascript
function getFilterState() {
    return {
        has_website: getTriToggle('website'),
        has_email: getTriToggle('email'),
        has_phone: getTriToggle('phone'),
        min_rating: parseFloat(ratingSlider.value),
        min_reviews: parseInt(reviewsSlider.value),
        is_claimed: getTriToggle('claimed'),
        has_photos: getTriToggle('photos'),
        category: categorySelect.value || null,
        price_level: getTriToggle('price'),
        zoom_level: getZoomLevel(),
        near_me: nearMeToggle.checked,
    };
}
```

- [ ] **Step 7: Commit**

```bash
git commit -m "feat(mapsearch): filter controls (toggles, sliders, selects)"
```

---

### Task 12: Results Table

**Files:**
- Create: `projects/mapsearch/app/static/js/table.js`

- [ ] **Step 1: Table rendering**

Function `renderTable(results)` — takes array of business objects, renders into HTML table. Columns: Business name, Category, City, Phone, Website, Email, Rating (stars), Reviews.

- [ ] **Step 2: Sortable columns**

Click column header → sort asc/desc. Show sort arrow indicator. Sort by: name (alpha), rating (numeric), reviews (numeric), city (alpha).

- [ ] **Step 3: Column toggle**

Dropdown to show/hide optional columns: Claimed, Photos, Price level, Lat/Lng, Google Maps link, Business status.

- [ ] **Step 4: Row hover highlights map pin**

- [ ] **Step 5: Results count header**

"618 results for Dentist in Manhattan, NY" — updates dynamically.

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(mapsearch): results table with sorting + column toggle"
```

---

### Task 13: Search Flow (Connect Everything)

**Files:**
- Create: `projects/mapsearch/app/static/js/app.js`

- [ ] **Step 1: Wire Search button to API**

Click Search → check if logged in → if not, show signup modal → if logged in, collect filters → POST /api/search → render results in table + pins on map.

- [ ] **Step 2: Loading state**

Show skeleton table + spinner while search runs.

- [ ] **Step 3: Error handling**

Insufficient credits → show "Buy credits" prompt. API error → toast notification. No results → empty state message.

- [ ] **Step 4: Results panel slide-in**

After search: results panel slides in from left, map shrinks to right side.

- [ ] **Step 5: Test full flow end-to-end**

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(mapsearch): full search flow — search → results → table + map"
```

---

### Task 14: i18n

**Files:**
- Create: `projects/mapsearch/app/static/js/i18n.js`

- [ ] **Step 1: Translation loader**

Detect browser language from `navigator.language`. Load matching JSON file (en/fr/es/de). Fallback to EN.

- [ ] **Step 2: Apply translations to DOM**

Use `data-i18n="key"` attributes on elements. On load, replace innerHTML with translated string.

**Important:** Export a `translateElement(el)` function that can be called after dynamic renders (e.g., after `table.js` renders new rows). Static elements are translated on page load; dynamic elements call `translateElement()` after insertion.

- [ ] **Step 3: Language selector in header**

Dropdown to override language. Save to localStorage.

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(mapsearch): i18n — EN/FR/ES/DE with browser auto-detect"
```

---

## Phase 2b: Credit Service (Task 15 — BEFORE Phase 3)

**Moved here from Phase 5.** The search service (Task 7) depends on credit deduction logic.

### Task 15: Credit Service

**Files:**
- Create: `projects/mapsearch/app/services/credit_service.py`
- Create: `projects/mapsearch/tests/test_credit_service.py`

- [ ] **Step 1: Write failing tests**

```python
def test_deduct_credits():
    """Deduct N credits from user, log transaction."""
    pass

def test_deduct_insufficient_raises():
    """Deducting more than balance raises error."""
    pass

def test_add_credits_purchase():
    """Add credits from Stripe purchase."""
    pass
```

- [ ] **Step 2: Implement credit_service.py**

```python
def deduct_credits(user_id, amount, reference_id, transaction_type="search"):
    """Deduct credits and log transaction. Raises if insufficient."""

def add_credits(user_id, amount, stripe_payment_id):
    """Add credits from purchase and log transaction."""

def get_balance(user_id):
    """Return current credit balance."""
```

- [ ] **Step 3: Run tests**

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(mapsearch): credit service — deduct, add, balance"
```

---

### Task 16: Stripe Credit Purchase

**Files:**
- Create: `projects/mapsearch/app/routers/credits.py`

- [ ] **Step 1: Define credit packs**

```python
CREDIT_PACKS = [
    {"id": "starter", "credits": 1000, "price_cents": 150, "label": "Starter"},
    {"id": "growth", "credits": 5000, "price_cents": 700, "label": "Growth"},
    {"id": "pro", "credits": 25000, "price_cents": 3200, "label": "Pro"},
    {"id": "agency", "credits": 100000, "price_cents": 12000, "label": "Agency"},
]
```

- [ ] **Step 2: Stripe Checkout session endpoint**

```
POST /api/credits/checkout
Body: { "pack_id": "growth" }
Response: { "checkout_url": "https://checkout.stripe.com/..." }
```

Creates Stripe Checkout session, redirects user.

- [ ] **Step 3: Stripe webhook endpoint**

```
POST /api/credits/webhook
```

**CRITICAL:** Verify webhook signature with `stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)`. Without this, anyone can POST fake purchase events. On `checkout.session.completed`: add credits to user, log transaction.

- [ ] **Step 4: Credit balance endpoint**

```
GET /api/credits/balance
Response: { "credits": 481 }
```

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(mapsearch): Stripe credit purchase + webhook"
```

---

### Task 17: Credits UI

**Files:**
- Create: `projects/mapsearch/app/static/js/credits.js`

- [ ] **Step 1: Credit balance display in header**

Amber pill showing current balance. Updates after each search.

- [ ] **Step 2: Credit purchase modal**

Show 4 credit packs with pricing. Click → redirect to Stripe Checkout.

- [ ] **Step 3: Insufficient credits prompt**

When search fails due to 0 credits → show purchase modal automatically.

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(mapsearch): credits UI — balance, purchase modal, prompts"
```

---

## Phase 6: Export + Auth UI (Tasks 18-19)

### Task 18: CSV Export

**Files:**
- Create: `projects/mapsearch/app/routers/export.py`

- [ ] **Step 1: Export endpoint**

```
GET /api/export/{search_id}
Response: CSV file download
```

Fetches all results for a search, streams as CSV. Free (no additional credits).

**SECURITY: Ownership check is mandatory.** Query must JOIN searches.user_id = authenticated user. If search_id belongs to a different user → 404 (not 403, to avoid confirming existence). UUIDs reduce guessing but do NOT replace authorization.

- [ ] **Step 2: Export button in results toolbar**

Click "Export CSV" → download starts.

- [ ] **Step 3: Log export in exports table**

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(mapsearch): CSV export (free, no extra credits)"
```

---

### Task 19: (MOVED to Task 9b — Auth Modal now in Phase 4)

---

## Phase 7: Deploy (Task 20)

### Task 20: VPS Deployment

**Files:**
- Create: `projects/mapsearch/deploy.sh`

- [ ] **Step 1: Create deploy script**

Model the deploy script on `scripts/deploy_vps.sh` with subcommands. Create `scripts/deploy_mapsearch.sh`:

```bash
#!/bin/bash
# Deploy MapSearch to VPS — mirrors deploy_vps.sh pattern
set -euo pipefail
VPS_HOST="${VPS_HOST:-82.21.4.94}"
VPS_DIR="/var/www/mapsearch"
COMMAND="${1:-help}"

case "$COMMAND" in
  app)
    echo "Deploying MapSearch app..."
    rsync -avz --delete projects/mapsearch/app/ "root@$VPS_HOST:$VPS_DIR/app/"
    rsync -avz projects/mapsearch/requirements.txt "root@$VPS_HOST:$VPS_DIR/"
    ssh "root@$VPS_HOST" "$VPS_DIR/venv/bin/pip install -q -r $VPS_DIR/requirements.txt"
    ssh "root@$VPS_HOST" "systemctl restart mapsearch"
    ;;
  quick)
    FILE="${2:?Usage: deploy_mapsearch.sh quick <relative-path>}"
    echo "Quick deploy: $FILE"
    scp "projects/mapsearch/$FILE" "root@$VPS_HOST:$VPS_DIR/$FILE"
    ssh "root@$VPS_HOST" "systemctl restart mapsearch"
    ;;
  deps)
    echo "Installing dependencies..."
    rsync -avz projects/mapsearch/requirements.txt "root@$VPS_HOST:$VPS_DIR/"
    ssh "root@$VPS_HOST" "$VPS_DIR/venv/bin/pip install -q -r $VPS_DIR/requirements.txt"
    ;;
  setup)
    echo "First-time setup..."
    ssh "root@$VPS_HOST" "mkdir -p $VPS_DIR && python3 -m venv $VPS_DIR/venv"
    rsync -avz --delete projects/mapsearch/app/ "root@$VPS_HOST:$VPS_DIR/app/"
    rsync -avz projects/mapsearch/requirements.txt "root@$VPS_HOST:$VPS_DIR/"
    ssh "root@$VPS_HOST" "$VPS_DIR/venv/bin/pip install -q -r $VPS_DIR/requirements.txt"
    echo "Now: copy .env.example to $VPS_DIR/.env and fill in values"
    ;;
  *)
    echo "Usage: deploy_mapsearch.sh {app|quick <file>|deps|setup}"
    ;;
esac

echo "Checking health..."
sleep 2
curl -sf "https://mapsearch.app/health" && echo " OK" || echo " FAILED"
```

**Database setup** also follows a script, not ad-hoc commands. Add to `setup` subcommand or a separate `scripts/setup_mapsearch_db.sh`:
```bash
#!/bin/bash
# One-time DB setup for MapSearch
set -euo pipefail
VPS_HOST="${VPS_HOST:-82.21.4.94}"
ssh "root@$VPS_HOST" "sudo -u postgres psql -c \"CREATE USER mapsearch WITH PASSWORD '\$MAPSEARCH_DB_PASSWORD';\""
ssh "root@$VPS_HOST" "sudo -u postgres psql -c \"CREATE DATABASE mapsearch OWNER mapsearch;\""
cat projects/mapsearch/app/database/schema.sql | ssh "root@$VPS_HOST" "sudo -u postgres psql mapsearch"
```

- [ ] **Step 2: Create systemd service on VPS**

```ini
[Unit]
Description=MapSearch FastAPI
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/mapsearch
ExecStart=/var/www/mapsearch/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8100
Restart=always
EnvironmentFile=/var/www/mapsearch/.env

[Install]
WantedBy=multi-user.target
```

- [ ] **Step 3: Add Caddy reverse proxy config**

```
mapsearch.app {
    reverse_proxy localhost:8100
}
```

- [ ] **Step 4: Create .env.example**

```
# MapSearch.app environment variables
MAPSEARCH_DATABASE_URL=postgresql://mapsearch:PASSWORD@82.21.4.94:5432/mapsearch
MAPSEARCH_SECRET_KEY=generate-with-openssl-rand-hex-32
DATAFORSEO_LOGIN=your-login
DATAFORSEO_PASSWORD=your-password
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
```

- [ ] **Step 5: Create venv on VPS**

```bash
ssh root@82.21.4.94 "python3 -m venv /var/www/mapsearch/venv"
ssh root@82.21.4.94 "/var/www/mapsearch/venv/bin/pip install -r /var/www/mapsearch/requirements.txt"
```

- [ ] **Step 6: Set up .env on VPS from .env.example**

- [ ] **Step 7: Verify port 8100 is free**

```bash
ssh root@82.21.4.94 "ss -tlnp | grep 8100"
```

- [ ] **Step 8: DNS setup** (after domain purchase)

Add A record: `mapsearch.app` → VPS IP. Wait for propagation. Caddy auto-provisions SSL.

- [ ] **Step 9: Deploy and verify**

```bash
./projects/mapsearch/deploy.sh
curl https://mapsearch.app/health
```
Expected: `{"status": "ok", "version": "1.0.0"}`

- [ ] **Step 10: Commit**

```bash
git commit -m "feat(mapsearch): VPS deployment + DNS + systemd service"
```

---

## Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 1 | 1-3 | Scaffolding + database + design assets |
| 2 | 4-5 | Auth (email/password + Google OAuth) |
| 2b | 15 | Credit service (BEFORE search — search depends on it) |
| 3 | 6, 6b, 7, 8 | Geocoder + location resolver + async DataForSEO client + search API |
| 4 | 9a-9c, 10-14, 9b | State module + auth modal + template + map + filters + table + search flow + i18n |
| 5 | 16-17 | Stripe payments + credits UI |
| 6 | 18 | CSV export |
| 7 | 20 | VPS deployment |

**Total: 22 tasks, ~90 steps.**

**Estimated duration:** 3-4 weeks with subagent-driven development (per reviewer, 2-3 weeks was optimistic).

**Dependencies (corrected):**
- Phase 2 (auth) depends on Phase 1 (DB)
- Phase 2b (credits) depends on Phase 1 (DB)
- Phase 3 (search) depends on Phase 1 + Phase 2 + Phase 2b
- Phase 4 frontend: Tasks 9a (state), 9b (auth modal) FIRST, then 10/11/12 in parallel, then 13 (search flow) after all three, then 14 (i18n)
- Phase 5 (Stripe) can run parallel with Phase 4
- Phase 6 (export) depends on Phase 3
- Phase 7 (deploy) depends on everything

**Parallelizable:**
- Tasks 4+5 || Task 6 || Task 6b (all only need DB)
- Tasks 10, 11, 12 (independent frontend modules)
- Task 16 || Task 14 (no dependencies)

## Review Fixes Applied

All issues from the code review have been addressed:

| Issue | Fix |
|-------|-----|
| location_code hardcoded to Switzerland | New Task 6b: location_resolver.py with 20-country mapping |
| Sync vs Async API | Committed to live/sync at $0.002/SERP. New async client, not shared scraper |
| psycopg2 blocks async | Replaced with asyncpg. All queries use $1/$2 params |
| Task ordering (auth modal, credit service) | Credit service moved to Phase 2b. Auth modal moved to Task 9b in Phase 4 |
| Credit rollback on API failure | Credits deducted AFTER successful API call, not before |
| No rate limiting | Added slowapi middleware + per-endpoint limits |
| No input validation | Added Pydantic request models |
| No CSRF / JWT security | JWT in httpOnly cookies (not localStorage). SameSite=Lax |
| No state management (frontend) | New Task 9a: state.js pub/sub module |
| INTERVAL syntax broken | Fixed to use make_interval() for asyncpg |
| No DataForSEO mock | Added tests/fixtures/ with canned response |
| No health check | Added GET /health endpoint |
| No DB user creation | Added CREATE USER + GRANT in Task 2 |
| No .env.example | Added to deploy task |
| No venv creation | Added to deploy task |
| Stripe webhook unsigned | Added signature verification note |
| 700 max not communicated | Added max_reached flag in search response |
| i18n on dynamic content | Added translateElement() re-apply note |
| Timeline too optimistic | Updated to 3-4 weeks |

**Deferred to v1.1:** Search history, saved searches, email templates, responsive mobile, Pingen integration.

## Round 2 Review Fixes (Codex findings)

| Finding | Fix |
|---------|-----|
| Cache key excludes filters → wrong results served | Split into `scrape_cache` (raw, keyed by keyword+location+zoom) and `searches` (per-user, with filters). Filters applied post-cache. |
| Credit burn on users who can't afford results | Credits = filtered result count (not raw). Check credits AFTER filtering, BEFORE delivering. "This search returns ~234 results. You have 10 credits." |
| IDOR on export endpoint | Ownership check: JOIN searches.user_id = authenticated user. Return 404 (not 403) for other users' searches. |
| Auth inconsistency (cookie vs header, no CSRF, no OAuth state) | All endpoints use httpOnly cookie (removed "JWT in header" reference). OAuth state param mandatory. Origin/Referer check on all POST endpoints. |
| Deploy script broken (requirements.txt not copied) | Fixed script to copy requirements.txt. Uses VPS_HOST env var. Health check after deploy. Follows repo deploy conventions. |
| Geocoder tests hit real Nominatim | All tests use mocked httpx responses. Canned fixtures in tests/fixtures/. |

**Credit model decision:** 1 credit = 1 filtered result. Filters reduce cost for users. We eat the DataForSEO cost for filtered-out rows (negligible at $0.002/SERP). This is BETTER than Outscraper which charges for all scraped results regardless.
