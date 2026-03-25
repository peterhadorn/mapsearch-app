# MapSearch.app — Master Plan

**Domain:** mapsearch.app
**Tagline:** "Search any area. Get every business."
**Product:** Beautiful web UI for searching Google Maps business data at scale. Search by keyword + location + radius, filter on 40+ fields, export as CSV. Powered by DataForSEO.

**Positioning:** NOT a "scraper" or "data extraction tool." This is "the business search engine Google should have built." Clean enough for a marketing assistant, powerful enough for an agency running 50 campaigns.

**Market:** Global product with Swiss version. EN/FR/ES/DE at launch.

---

## Table of Contents

1. [Product Vision](#1-product-vision)
2. [Core User Flow](#2-core-user-flow)
3. [Feature Definition](#3-feature-definition)
4. [Technical Architecture](#4-technical-architecture)
5. [Data Model](#5-data-model)
6. [Internationalization](#6-internationalization)
7. [Pricing & Business Model](#7-pricing--business-model)
8. [Competitive Moat](#8-competitive-moat)
9. [Go-to-Market](#9-go-to-market)
10. [Phases & Roadmap](#10-phases--roadmap)
11. [Open Questions](#11-open-questions)

---

## 1. Product Vision

### The Problem

People who need bulk business data from Google Maps today face:

- **Too technical**: API-first tools (Outscraper, Bright Data) with API keys, JSON, webhooks
- **Too limited**: Chrome extensions that break, cap at 100 results, no real filtering
- **Too expensive**: Enterprise platforms (PhantomBuster, Clay) at $50-350/mo for basic needs
- **Too ugly**: Every tool looks like a developer console, not a product

### The Opportunity

Nobody has built the **"Airtable for Google Maps data"** — a clean, gorgeous interface where:
1. You draw a circle on a map and type a keyword
2. Results appear instantly in a beautiful, filterable data table
3. You export exactly what you need
4. You pay only for what you use

### Who Is This For?

Everyone equally — the tool is generic, use cases self-select:

| User | Use Case |
|------|----------|
| Direct mail companies | Need addresses + names by industry + area for physical mailings |
| Freelance web designers | Find businesses with no/bad website |
| Marketing agencies | Build prospect lists by niche + city |
| Sales reps / SDRs | Territory mapping, cold call lists |
| Market researchers | Competitor analysis, market sizing |
| Local service businesses | Find suppliers/partners in their area |
| Real estate agents | Business density analysis |

### What Makes MapSearch Different

1. **No login to browse.** See the map, set location, type keyword — signup only when you search.
2. **Every field is filterable.** Website yes/no, email yes/no, rating range, review count, claimed/unclaimed, photos, price level. Combine any filters.
3. **No jargon.** No "API credits", "execution minutes", "phantoms", "actors." Just: search, filter, download.
4. **No subscription.** Buy credits, use them whenever. No monthly commitment, no expiring quotas.
5. **Beautiful.** Clean modern UI. Not a developer tool. Something you'd show a client.
6. **Instant.** Results in 3-5 seconds, not queued batch jobs.
7. **Multilingual.** EN/FR/ES/DE from day one. Auto-detects browser language.

---

## 2. Core User Flow

```
1. LAND → MapSearch.app
   Full-screen map (OpenStreetMap/Leaflet), muted/dark theme.
   Prominent search bar floating center-top.
   Language auto-detected from browser (EN/FR/ES/DE).

2. EXPLORE (no account needed)
   - Click/drag map to set location, or type a city name
   - Type keyword ("Dentist", "Restaurant", "Metallbau")
   - See the interface, feel the product

3. SET FILTERS (before search)
   - Has website: Yes / No / Any
   - Has email: Yes / No / Any
   - Rating: min/max slider
   - Review count: min/max
   - Category refinement
   - Claimed/unclaimed
   - Price level
   - Radius (post-search filter, applied client-side)

4. SEARCH → Signup wall
   Hit search → modal: "Create free account (99 free credits)"
   - Google OAuth (one click)
   - Email + password
   - 10 seconds to account creation

5. CREDITS CHARGED → RESULTS DELIVERED
   - Credits deducted immediately based on result count
   - DataForSEO called with pre-search filters applied
   - Results delivered as: CSV download + live table view
   - Table is our UX bonus (Outscraper only gives file download)
   - Map pins appear for geographic context
   - Clicking a row highlights pin on map

6. POST-SEARCH REFINEMENT
   - Radius filtering (client-side, on already-loaded data)
   - Additional column sorting
   - No extra credits — data is already paid for

7. BUY MORE
   - Credits run out → "Buy more credits" → Stripe checkout
   - Credit packs at $1.50/1,000 base rate
```

### Anti-Abuse Measures

- Google OAuth or verified email required before any search
- Rate limiting: max N searches per minute
- Credit system naturally limits abuse (99 free credits = just enough to taste)
- No data displayed until credits are charged (same model as Outscraper)

---

## 3. Feature Definition

### MVP (v1.0) — "Search, Filter, Export"

| Feature | Details |
|---------|---------|
| Full-screen map | Leaflet.js + OpenStreetMap tiles |
| Location selector | Click map, type city, or drag circle for radius |
| Radius control | Slider (1-50km) or draggable circle on map |
| Keyword search | Free text, searches Google Maps categories |
| Signup wall | Google OAuth + email/password, 50 free credits |
| Results table | Sortable columns, pagination or virtual scroll |
| Map pins | Pins for results, click pin = highlight row |
| Power filters | See filter list below |
| CSV export | Filtered results, costs credits |
| Credit system | Per-result pricing, Stripe for purchases |
| 4 languages | EN/FR/ES/DE, browser auto-detect |
| Responsive | Works on desktop + tablet (mobile = limited) |

### Power Filters (MVP)

| Filter | Type | Source |
|--------|------|--------|
| Has website | Yes / No / Any | Computed from domain field |
| Has email | Yes / No / Any | Computed from email field |
| Has phone | Yes / No / Any | Computed from phone field |
| Google rating | Range slider (1.0 - 5.0) | `rating` |
| Review count | Range slider (0 - 1000+) | `reviews_count` |
| Category | Dropdown / multi-select | `category` + `additional_categories` |
| Google listing claimed | Yes / No / Any | `is_claimed` from DataForSEO |
| Has photos | Yes / No / Any | Computed from `photos_count` |
| Price level | €/€€/€€€/€€€€ | `price_level` |

### Data Columns (MVP)

| Column | Always Visible | Toggleable |
|--------|---------------|------------|
| Business name | Yes | |
| Category | Yes | |
| Address / City | Yes | |
| Phone | Yes | |
| Website | Yes | |
| Email | Yes | |
| Google rating | Yes | |
| Review count | Yes | |
| Claimed | | Yes |
| Photos count | | Yes |
| Price level | | Yes |
| Latitude/Longitude | | Yes |
| Google Maps link | | Yes |
| Business status | | Yes |

### v1.1 — "Smart Features"

| Feature | Details |
|---------|---------|
| Saved searches | Re-run a search later, see new results |
| Search history | Dashboard of past searches |
| Column visibility toggle | Show/hide any column |
| Bulk select + export | Check rows, export selection |
| Category filter autocomplete | Type to filter categories |

### v2.0 — "Intelligence Layer"

| Feature | Details |
|---------|---------|
| Monitoring alerts | "New businesses matching X" notifications |
| Website quality score | Rate the business's website (from our WebEvolve tech) |
| Enrichment: owner email | Find decision-maker email (AnyMailFinder/pattern matching) |
| NOGA classification | Swiss industry codes (unique to us) |
| Handelsregister cross-ref | Swiss commercial registry data |
| Review rank tracking | One Trick-style rank monitoring as upsell |

### v3.0 — "Platform"

| Feature | Details |
|---------|---------|
| API access | REST API for developers/agencies |
| Pingen integration | Search → filter → send physical letters via Pingen API |
| Team accounts | Shared credits, user management |
| Google Sheets integration | Push results directly to Sheets |
| Zapier/Make integration | Automate workflows |
| CRM integrations | Push leads to HubSpot, Salesforce, Twenty |
| White-label | Agencies resell under their brand |

---

## 4. Technical Architecture

### System Overview

```
                    ┌─────────────────────────────────────┐
                    │         mapsearch.app                │
                    │    (Caddy reverse proxy, VPS)        │
                    └─────────────┬───────────────────────┘
                                  │
                    ┌─────────────▼───────────────────────┐
                    │       FastAPI Application            │
                    │                                      │
                    │  ┌──────────┐  ┌──────────────────┐  │
                    │  │ Auth     │  │ Search API       │  │
                    │  │ (OAuth + │  │ /api/search      │  │
                    │  │ session) │  │ /api/export      │  │
                    │  └──────────┘  └────────┬─────────┘  │
                    │                         │            │
                    │  ┌──────────┐  ┌────────▼─────────┐  │
                    │  │ Stripe   │  │ DataForSEO       │  │
                    │  │ Webhooks │  │ (reuse shared/)  │  │
                    │  └──────────┘  └──────────────────┘  │
                    │                                      │
                    │  ┌──────────────────────────────┐    │
                    │  │ PostgreSQL (mapsearch DB)     │    │
                    │  │ - users, searches, credits    │    │
                    │  └──────────────────────────────┘    │
                    └──────────────────────────────────────┘
```

### Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Backend | FastAPI (Python 3) | Same as leadgen, reuse shared modules |
| Frontend | Vanilla JS + Leaflet.js | No build step, ship fast, add framework later if needed |
| Templates | Jinja2 | Server-rendered base, JS for interactive parts |
| Map | Leaflet.js + OpenStreetMap | Free, no API key, good enough |
| Database | PostgreSQL | Same as leadgen, proven |
| Payments | Stripe Checkout | One-time credit packs, no subscriptions to manage |
| Auth | Google OAuth2 + email/password | Google = one click, email = fallback |
| Reverse proxy | Caddy | Auto-SSL, same as existing VPS |
| Hosting | VPS (start on existing, scale to US VPS) | Full control, cheap at scale |
| i18n | JSON translation files | Simple key-value, no framework needed |
| Data source | DataForSEO Google Maps API | $0.002/result, 40+ fields, fast |

### Key Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate app or extend leadgen? | Separate FastAPI app in `projects/mapsearch/` | Different auth model (public signups), different deployment, clean separation |
| Own DB or share? | Own PostgreSQL DB | Different data model, different users. Reuse DataForSEO scraper code via shared/ imports. |
| Frontend framework? | Vanilla JS + Leaflet (MVP) | Ship in days, not weeks. No build step. Upgrade to React/Vue only if complexity demands it. |
| Cache strategy? | Cache search results 24-72h | Same keyword+location+radius = free cache hit. Reduces DataForSEO costs dramatically at scale. |
| Repo location | `projects/mapsearch/` in leadgen monorepo | Reuse shared/ modules (DataForSEO scraper, DB patterns, NOGA) |
| VPS | Start on existing VPS (82.21.4.94), scale later | Test with real users before investing in infrastructure |

### Reusable Components from Leadgen Monorepo

| Component | Source | Reuse Level |
|-----------|--------|-------------|
| DataForSEO Google Maps scraper | `shared/scrapers/scrape_dataforseo.py` | Direct import |
| NOGA classification | `shared/utils/noga_lookup.py` | Direct import (v2) |
| Email enrichment | `shared/enrichment/` | Direct import (v2) |
| DB client patterns | `shared/utils/db_client.py` | Pattern reuse, new DB |
| Security middleware | `backend/main.py` | Copy CORS, headers, rate limiting |
| Stripe webhook patterns | `backend/routers/gmb/webhook_handler.py` | Pattern reuse |

---

## 5. Data Model

### Users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),           -- NULL for OAuth-only users
    name VARCHAR(255),
    google_id VARCHAR(255) UNIQUE,        -- Google OAuth subject ID
    credits_remaining INTEGER DEFAULT 99, -- Signup bonus
    locale VARCHAR(5) DEFAULT 'en',       -- en, fr, es, de
    stripe_customer_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);
```

### Searches (Cache + History)

```sql
CREATE TABLE searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    keyword VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,       -- City name or "lat,lng"
    radius_km INTEGER DEFAULT 10,
    country VARCHAR(10),                  -- Auto-detected or user-selected
    result_count INTEGER,
    credits_used INTEGER,
    cache_key VARCHAR(500) GENERATED ALWAYS AS (
        lower(trim(keyword)) || '|' || lower(trim(location)) || '|' || radius_km || '|' || lower(coalesce(country, ''))
    ) STORED,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_searches_cache ON searches(cache_key, created_at DESC);
```

### Search Results (Cached Data)

```sql
CREATE TABLE search_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    search_id UUID REFERENCES searches(id) ON DELETE CASCADE,
    -- Core
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
    -- Google Maps
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
    -- Extended
    latitude NUMERIC(10,7),
    longitude NUMERIC(10,7),
    price_level VARCHAR(10),
    work_hours JSONB,
    business_status VARCHAR(50),
    rating_distribution JSONB,
    -- Computed for fast filtering
    has_website BOOLEAN GENERATED ALWAYS AS (domain IS NOT NULL AND domain != '') STORED,
    has_email BOOLEAN GENERATED ALWAYS AS (email IS NOT NULL AND email != '') STORED,
    has_phone BOOLEAN GENERATED ALWAYS AS (phone IS NOT NULL AND phone != '') STORED
);

CREATE INDEX idx_results_search ON search_results(search_id);
CREATE INDEX idx_results_filters ON search_results(has_website, has_email, rating, reviews_count);
```

### Credit Transactions

```sql
CREATE TABLE credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    amount INTEGER NOT NULL,              -- positive = add, negative = spend
    type VARCHAR(50) NOT NULL,            -- 'signup_bonus', 'purchase', 'search', 'export'
    reference_id UUID,                    -- search_id or export_id
    stripe_payment_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Exports

```sql
CREATE TABLE exports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    search_id UUID REFERENCES searches(id),
    row_count INTEGER,
    filters_applied JSONB,
    credits_used INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 6. Internationalization

### Strategy

- 4 languages at launch: English, French, Spanish, German
- Auto-detect from `Accept-Language` browser header
- English fallback for all other languages
- User can override via language selector (saved to profile)
- All UI strings in JSON translation files
- DataForSEO returns localized category names based on search location

### Translation File Structure

```
projects/mapsearch/app/i18n/
├── en.json
├── fr.json
├── es.json
└── de.json
```

### Translation Scope (MVP)

- UI labels (buttons, headers, filter names, tooltips)
- Error messages
- Signup/login flow
- Credit purchase flow
- Email templates (welcome, purchase receipt)
- NOT: category names (come from Google, already localized)
- NOT: business data (pass-through from DataForSEO)

---

## 7. Pricing & Business Model

### Demolish the Competition

Our backend cost is **$0.20 per 1,000 results** (DataForSEO). Here's what competitors charge:

| Competitor | Price per 1,000 records | Type |
|------------|------------------------|------|
| **Outscraper** | $3.00 | Direct comp (self-serve, same buyer) |
| **Bright Data** | $2.50 | Enterprise/infrastructure ($250 min order) |
| **Apify** | $2.10 - $4.00 | Actor-dependent, confusing pricing |
| **MapsLeads** | ~$3.25 | Unclear, limited |
| **MapSearch.app** | **$1.50** | **2x cheaper than Outscraper, 87% margin** |

**We charge $1.50/1,000 results and make 87% margins.** Still 2x cheaper than Outscraper. Room to drop to $1.00 as a promo later.

### Why We Win (Not Just on Price)

| Dimension | Outscraper | MapSearch.app |
|-----------|-----------|---------------|
| Price | $3/1,000 | **$1.50/1,000 (2x cheaper)** |
| UI | Developer tool, task queue | **Beautiful map + live filterable table** |
| Workflow | Submit job → wait → download CSV → open Excel | **Type → search → filter → export. Done.** |
| Map view | None | **Full interactive map with pins** |
| Languages | English only | **EN/FR/ES/DE from day one** |
| Free tier | 25 records | **99 records** |
| Export | Separate cost | **Free (already paid on search)** |
| Time to first result | Minutes (queued job) | **Seconds (live)** |

**The demolition formula: 2x cheaper + 10x prettier + 10x simpler + multilingual + map view = why would anyone use Outscraper?**

### Cost Structure

| Action | DataForSEO Cost | Notes |
|--------|----------------|-------|
| 1 search (100 results) | ~$0.02 | Charged per 100 results |
| 1 search (500 results) | ~$0.10 | 5 x $0.02 |
| 1 search (1,000 results) | ~$0.20 | |
| Cached search (repeat) | $0.00 | 24-72h cache |

### Pricing Model: Per-Result Credits

**1 credit = 1 result row returned from a search.**

A search for "Dentist Zürich" returning 618 results costs the user 618 credits.

### Credit Packs

| Pack | Credits | Price | Per 1,000 | Margin | vs Outscraper ($3/1k) |
|------|---------|-------|-----------|--------|----------------------|
| **Free (signup)** | 99 | $0 | Free | — | They give 25 |
| **Starter** | 1,000 | $1.50 | $1.50 | 87% | 2x cheaper |
| **Growth** | 5,000 | $7 | $1.40 | 86% | 2x cheaper |
| **Pro** | 25,000 | $32 | $1.28 | 84% | 2x cheaper |
| **Agency** | 100,000 | $120 | $1.20 | 83% | 2.5x cheaper |

**Consistently 2x cheaper than Outscraper at every tier, with 83-87% margins.** Simple story: "Half the price, 10x the product."

### For Context: What $100 Gets You

| Platform | Records for $100 |
|----------|-----------------|
| Bright Data | 40,000 (but $250 minimum) |
| Outscraper | 33,333 |
| MapsLeads | ~30,769 |
| Apify | 25,000-47,000 (confusing) |
| **MapSearch.app** | **66,667 (Starter) to 83,333 (Agency)** |

**Consistently ~2x more records per dollar than Outscraper.**

### Revenue Projections (Conservative)

| Scenario | Users | Avg spend/mo | MRR | DataForSEO cost/mo | Margin |
|----------|-------|-------------|-----|---------------------|--------|
| Early (month 3) | 50 | $10 | $500 | ~$50 | 90% |
| Growth (month 6) | 200 | $15 | $3,000 | ~$300 | 90% |
| Scale (month 12) | 1,000 | $20 | $20,000 | ~$2,000 | 90% |

**Even at scale, DataForSEO cost is ~10% of revenue. The rest is margin.**

### What's Free

- Browse the map, set location, see the interface
- Account creation
- 99 credits on signup (enough for one real search — Outscraper only gives 25)

### What Costs Credits

- Each search: 1 credit per result row returned
- CSV export: **FREE** (already paid for the search — one less friction point vs Outscraper)

### Alternative Considered: Pay-per-export

Rejected. If search is free but export costs, users screenshot the table. Per-result-on-search is cleaner and prevents abuse. Plus, free export is a competitive advantage — Outscraper charges separately for export.

---

## 8. Competitive Moat

### Short-term (0-6 months): UX + Price Disruption

The data is commoditized (DataForSEO sells to everyone). The moat is:
- **2x cheaper** than the direct competitor (Outscraper at $3/1,000 vs our $1.50/1,000)
- **10x prettier** — beautiful map + live table vs developer console
- **10x simpler** — type, search, filter, export vs task queues and API keys
- **Multilingual from day one** — EN/FR/ES/DE, competitors are English-only
- **Free export** — Outscraper charges separately, we don't

### Medium-term (6-12 months): Swiss/DACH Specialization

Layer on unique data we already have:
- NOGA industry classification (Swiss-specific)
- Handelsregister cross-referencing
- Website quality scoring (WebEvolve tech)
- Swiss market expertise in sales & support

### Long-term (12+ months): Intelligence + Integrations

Graduate from "search tool" to "business intelligence platform":
- Opportunity scoring ("this business needs a new website")
- Market monitoring alerts ("3 new restaurants in your area")
- Decision-maker enrichment (find the owner, not info@)
- Pingen integration (search → filter → send physical letters)
- CRM push (HubSpot, Salesforce, Twenty)
- API access for developers

### What Is NOT a Moat

- The data itself (DataForSEO sells to everyone)
- Basic filtering (trivially copyable)
- CSV export (commodity feature)

---

## 9. Go-to-Market

### Phase 1: Swiss Launch

- Peter's network: agencies, freelancers, direct mail companies
- Case study from metal client (real results, real numbers)
- Swiss B2B email list from existing leadgen pipeline
- LinkedIn content (Peter's profile)

### Phase 2: Organic Growth

- SEO: target "Google Maps data export", "find businesses by location", "bulk business search"
- YouTube: "How to find 500 dentists in any city in 30 seconds" demo videos
- Content marketing: "How direct mail companies get addresses" blog posts
- Product Hunt launch

### Phase 3: Paid + Partnerships

- Google Ads on competitor keywords
- Affiliate program (10-20% recurring)
- Agency partnerships (white-label option)
- Integration directory listings (Zapier, Make)

---

## 10. Phases & Roadmap

### Phase 1: MVP (2-3 weeks)

Build the core search + filter + export flow:

1. Project scaffolding (FastAPI app in `projects/mapsearch/`)
2. Database schema + migrations
3. Google OAuth + email/password auth
4. Landing page with map (Leaflet + OpenStreetMap)
5. Search flow (keyword + location + radius → DataForSEO)
6. Results table (sortable, filterable)
7. Map pins (click row → highlight pin, click pin → highlight row)
8. Power filters (all MVP filters)
9. CSV export + credit deduction
10. Stripe credit purchase (one-time packs)
11. i18n (EN/FR/ES/DE)
12. Deploy to VPS

### Phase 2: Polish (1-2 weeks)

- Search history dashboard
- Saved searches
- Column visibility toggle
- Loading states + animations
- Error handling + edge cases
- Mobile responsive (read-only, no search on mobile)
- Cache optimization (24-72h result caching)

### Phase 3: Intelligence (month 2-3)

- Website quality scoring
- NOGA classification (Swiss data)
- Enrichment: owner email
- Monitoring alerts

### Phase 4: Platform (month 4-6)

- API access
- Pingen integration
- Team accounts
- CRM integrations

---

## 11. Decisions Log

| # | Question | Decision |
|---|----------|----------|
| 1 | Credit pricing | **$1.50/1,000 results.** 2x cheaper than Outscraper ($3/1k). 87% margin. |
| 2 | Does DataForSEO `is_claimed` work reliably? | **OPEN — test needed.** |
| 3 | Cache duration | **72h minimum.** Business data doesn't change hourly. |
| 4 | Search area / zoom | **Pre-search param.** Maps to DataForSEO zoom levels: Neighborhood (~3 mi / z14), District (~6 mi / z13), City (~12 mi / z12), Metro (~25 mi / z11). User picks one before searching. Affects API call and cost. |
| 5 | Pingen integration | **v3.** Not day 1. |
| 6 | Domain: mapsearch.app | **PENDING purchase.** |
| 7 | VPS | **Start on existing Swiss VPS (82.21.4.94)** for testing. US VPS when going to production. |
| 8 | Max results per search | **700 max** (DataForSEO depth limit). No confirmation needed. |
| 9 | Pre-search filters | **YES — filters set BEFORE hitting DataForSEO.** Reduces results, saves credits, saves API cost. |
| 10 | Anti-screenshot / data display | **Non-issue.** Same model as Outscraper: filters first → credits charged → results delivered (CSV download + live table view). No data on screen until paid. Table view is our bonus UX on top of Outscraper's download-only model. |
| 11 | Zoom factor strategy | **User chooses.** 4 options: Neighborhood (z14, ~3mi), District (z13, ~6mi), City (z12, ~12mi), Metro (z11, ~25mi). |
| 12 | Near Me mode | **Toggle in search card.** Switches from keyword+location to DataForSEO `near_me` query strategy. Simulates "dentist near me" as Google shows it. Requires geocoding location → lat/lng coordinates (use Nominatim/OpenStreetMap geocoder, free). |

---

## Origin

This plan evolved from the original LocalLeads exploration (`plans/explorations/2026-02-06-google-maps-search-saas.md`). Key changes:

- Renamed from LocalLeads to **MapSearch.app**
- Repositioned from Swiss-first to **global product with Swiss version**
- Added 4-language support (EN/FR/ES/DE)
- Changed auth flow to **signup-before-search** (Option B)
- Confirmed **table-first UI** (map is context, not primary)
- Added Pingen integration to roadmap (v3)
- Added `is_claimed` filter (confirmed DataForSEO supports it)
- Updated pricing model to **per-result credits** (not per-search)
