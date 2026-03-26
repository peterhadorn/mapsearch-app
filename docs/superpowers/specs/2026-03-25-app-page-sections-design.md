# App Page Sections — Design Spec

**Date:** 2026-03-25
**Status:** Approved

## Overview

Add Features, Pricing, How it works, CTA, and Footer sections below the existing map/search area in `app.html`. Add navigation items to the header that smooth-scroll to each section. Everything lives in the single-page app — no new routes.

## Header Navigation

Current header: `MapSearch [logo]` ... `EN | 99 credits | theme | Sign In`

Add nav links after logo: **Features | Pricing | How it works**

These are anchor links (`#features`, `#pricing`, `#how-it-works`) with smooth scroll behavior.

## Section 1: Features (`#features`)

One section with three visual blocks, stacked vertically.

### Block 1 — Tool Capabilities

Section label: "Features"
Headline: "Everything you need to find businesses at scale"

6 feature cards in a 2x3 or 3x2 grid:

1. **Real-time results** — "Results in seconds, not hours. No task queues, no waiting."
2. **10+ filters** — "Website, email, phone, rating, reviews, claimed, photos, price, category. Pay only for what passes your filters."
3. **CSV export** — "Download your results as CSV. Free with every search."
4. **Interactive map** — "See every result on a live map. Click pins, hover rows."
5. **4 languages** — "EN, FR, DE, ES. Auto-detects your browser language."
6. **Smart cache** — "Same search within 72h costs zero extra credits."

### Block 2 — Data Fields

Headline: "40+ data points per business"

Visual grid showing the actual field names in pill/tag style:
Business name, Category, Address, City, State, ZIP, Country, Phone, Email, Domain, URL, Rating, Reviews count, Is claimed, Verified, Photos count, Main image, Latitude, Longitude, Google Maps URL, Price level, Work hours, Business status, Rating distribution, Additional categories, Category IDs, Place ID, CID

### Block 3 — Why MapSearch

Headline: "Same data. Half the price. Better experience."

Simple comparison layout (not a full table — keep it punchy):
- **2x cheaper** — "$1.50/1,000 vs Outscraper's $3/1,000"
- **Instant results** — "Real-time API, not async task queues"
- **No API keys** — "Just sign up and search. No developer setup."
- **Filters save money** — "618 raw results → 234 with email → pay for 234, not 618"

## Section 2: Pricing (`#pricing`)

Section label: "Pricing"
Headline: "Pay as you go. No subscriptions."
Subtitle: "1 credit = 1 filtered result. Filters save you money."

5 pricing cards in a horizontal row (wraps on mobile):

| Pack | Credits | Price | Per 1,000 | CTA |
|------|---------|-------|-----------|-----|
| Free | 99 | $0 | — | "Get started" → signup modal |
| Starter | 1,000 | $1.50 | $1.50 | "Buy" → Stripe checkout |
| Growth | 5,000 | $7.00 | $1.40 | "Buy" → Stripe checkout |
| Pro | 25,000 | $32.00 | $1.28 | "Buy" → Stripe checkout |
| Agency | 100,000 | $120.00 | $1.20 | "Buy" → Stripe checkout |

Growth card gets a "Popular" badge.

Buy buttons: if logged in → Stripe checkout. If not logged in → signup modal, then redirect to Stripe after signup.

## Section 3: How It Works (`#how-it-works`)

Section label: "How it works"
Headline: "Three steps. That's it."
Subtitle: "No API keys. No task queues. No waiting."

Three numbered steps with icons:
1. **Search** — "Enter a keyword and location. We search Google Maps in real time."
2. **Filter** — "Narrow results with 10+ filters. Only pay for what passes."
3. **Export** — "Download CSV or browse the interactive table + map."

## Section 4: CTA

Full-width section with accent background gradient.

Headline: "Ready to find every business in your area?"
Subtitle: "99 free credits. No credit card required."
Button: "Sign up for free" → opens signup modal

## Section 5: Footer

Minimal footer:
- Left: "© 2026 MapSearch"
- Right: language selector (duplicated from header for convenience)

## Technical Notes

### Files to modify
- `app/templates/app.html` — add all sections after the signup modal, before `{% endblock %}`
- `app/static/css/app.css` — section styles (port relevant CSS from `design/html/landing.html`)
- `app/templates/base.html` — no changes needed (sections are in app.html)

### Files NOT to create
- No new routes. No new JS files. Everything is HTML + CSS in the existing template.
- Pricing "Buy" buttons reuse the existing `Credits.purchase(packId)` function from `credits.js`
- CTA button reuses `Auth.showModal()` from `auth.js`

### Smooth scroll
Add `scroll-behavior: smooth` to `html` element. Nav links use standard `<a href="#features">`.

### Mobile
- Feature cards: 1 column on mobile, 2 on tablet, 3 on desktop
- Pricing cards: 1 column on mobile, scrollable horizontal on tablet, 5 across on desktop
- How it works: stack vertically on mobile
- Header nav items: collapse into hamburger on mobile (or hide — the sections are scrollable anyway)

### i18n
All text uses `data-i18n` attributes. Translation keys need to be added to the 4 JSON files. Can be done in a follow-up task.

### Design reference
Port styles from `design/html/landing.html` where applicable (section spacing, pricing cards, step cards). Adapt to match the existing app.css design system (accent colors, glass effects, etc.).
