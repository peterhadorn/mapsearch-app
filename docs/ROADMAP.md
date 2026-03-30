# MapSearch.app — Production Roadmap

Last updated: 2026-03-30

## Current State

The app is deployed and running at https://mapsearch.app. The full backend is built:
search, filtering, credit system, Stripe payments, CSV export, admin panel, auth.

**What works right now:**
- User signup/login (email + password, JWT)
- Search Google Maps via DataForSEO (up to 700 results)
- Filter results (website, email, phone, rating, price level)
- Credit deduction (1 credit = 1 filtered result)
- Stripe Checkout (credit pack purchase)
- CSV export (free with every search)
- Search history + re-run
- Admin panel (users, searches, revenue)
- Password reset (needs SMTP configured)
- Soft delete accounts (30-day purge)

**Infrastructure:**
- VPS: 82.21.4.94, Caddy reverse proxy, systemd service
- Database: PostgreSQL (8 tables, indexed)
- Domain: mapsearch.app (DNS direct, Caddy SSL)
- All env vars configured (DataForSEO, Stripe, DB, JWT secret)

---

## Phase 1: Launch-Ready (1-2 hours)

Must-do before sharing with anyone.

- [ ] **Update credit packs in `credits.py`** to match new pricing:
  - Starter: 5,500 credits / $10 ($1.80/1k)
  - Growth: 30,000 credits / $50 ($1.67/1k)
  - Pro: 65,000 credits / $100 ($1.54/1k)
  - Agency: 666,000 credits / $1,000 ($1.50/1k)
- [ ] **Update `SIGNUP_BONUS_CREDITS`** from 99 to 100 in `config.py`
- [ ] **Verify Stripe webhook URL** is set to `https://mapsearch.app/api/credits/webhook` in Stripe dashboard
- [ ] **Test full flow** — signup, search "dentist" in "Basel", apply email filter, export CSV
- [ ] **Test Stripe** — buy Starter pack, verify credits arrive, check webhook logs
- [ ] **Deploy**

---

## Phase 2: Before Sharing (1 evening)

Critical for credibility. Without email, users can't reset passwords.

- [ ] **Email setup** (password reset emails):
  - Create `noreply@mapsearch.app` in cPanel
  - Add MX + mail A record in Cloudflare (DNS only, grey cloud)
  - Add SPF, DKIM, DMARC TXT records
  - Set email routing to Local in cPanel
  - Configure SMTP env vars on VPS (.env)
  - Test password reset end-to-end
  - (Full checklist in TODO.md)
- [ ] **Error monitoring** — add Sentry or structured JSON logging
- [ ] **Stripe idempotency** — add dedup check on webhook (payment_intent ID) to prevent double-crediting on retries

---

## Phase 3: Growth Features (next weeks)

Not blocking launch, but improve conversion and stickiness.

- [ ] **Location autocomplete** — Mapbox geocoding (100k/month free, $0.75/1k after)
- [ ] **Search language filter** — let users search Google Maps in specific languages
- [ ] **Google OAuth** — "Sign in with Google" (currently email/password only)
- [ ] **Email verification on signup** — confirm email before granting free credits
- [ ] **i18n translations** — update DE/FR/ES JSON files with new copy
- [ ] **Competitor comparison pages** — SEO content: "MapSearch vs Outscraper", etc.
- [ ] **API documentation** — REST API for power users/developers

---

## Phase 4: Scale (when traction)

Only invest here once there's paying users.

- [ ] **Usage analytics** — track searches, conversion, churn
- [ ] **Referral program** — "Give 100 credits, get 100 credits"
- [ ] **Bulk/scheduled exports** — recurring searches for agency clients
- [ ] **Rate limiting per user** — prevent abuse of free tier
- [ ] **DataForSEO retry logic** — handle API timeouts gracefully
- [ ] **Multi-worker deployment** — Gunicorn with multiple uvicorn workers
- [ ] **Database connection pooling** — PgBouncer if connection count grows

---

## Pricing

| Pack | Credits | Price | Per 1,000 |
|------|---------|-------|-----------|
| Free | 100 | $0 | On signup |
| Starter | 5,500 | $10 | $1.80 |
| Growth | 30,000 | $50 | $1.67 |
| Pro | 65,000 | $100 | $1.54 |
| Agency | 666,000 | $1,000 | $1.50 |

Competitors (Outscraper, PhantomBuster) charge $3+/1,000. We're half that at every tier.

---

## Go-to-Market Options

Peter's marketing energy is going to AISO. MapSearch needs an alternative GTM path.

**Low-effort (do once):**
- Product Hunt launch
- Post on Indie Hackers, r/SaaS, r/leadgeneration, r/coldoutreach
- List on BetaList, MicroLaunch, SaaSHub
- LinkedIn post (Peter's network)

**Passive/compounding:**
- SEO comparison pages (vs Outscraper, PhantomBuster, Apify)
- Google Ads on "google maps scraper" / "google maps leads" keywords
- AI SEO optimization (get cited by ChatGPT/Perplexity for lead gen tools)

**Partnership model:**
- Find a growth/marketing partner in the lead gen space
- Revenue share: 30-40% for whoever drives users
- Ideal partner: someone who already sells to agencies/sales teams
- They'd both USE and PROMOTE the tool

---

## Architecture Notes

- **Backend:** FastAPI + asyncpg + PostgreSQL
- **Frontend:** Vanilla JS + Jinja2 + Leaflet.js
- **Data:** DataForSEO Google Maps Live API
- **Payments:** Stripe Checkout (one-time packs, not subscriptions)
- **Auth:** JWT in httpOnly cookies, bcrypt passwords
- **Cache:** scrape_cache table (72h TTL, dedup by keyword+location+zoom)
- **Deploy:** rsync to VPS, systemd service, Caddy SSL
