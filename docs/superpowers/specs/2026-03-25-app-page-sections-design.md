# App Page Sections — Design Spec

**Date:** 2026-03-25
**Status:** Approved

## Overview

Add Features, Pricing, How it works, CTA, and Footer sections below the existing map/search area in `app.html`. Add navigation items to the header that smooth-scroll to each section. Everything lives in the single-page app — no new routes.

## Page Structure

The current app is entirely `position: fixed` layers (header, map, overlay, search card). To add scrollable sections below, the page needs restructuring:

1. **Hero wrapper** (`<div class="hero-viewport">`) — wraps the existing map + overlay + search card. Set to `height: 100vh; position: relative; overflow: hidden`. The map, overlay, and search card move INSIDE this wrapper and change from `position: fixed` to `position: absolute` (relative to the wrapper).
2. **Header stays `position: fixed`** — it floats over everything, z-index above all sections.
3. **Sections flow naturally** below the hero wrapper as normal document flow. User scrolls past the 100vh hero into Features, Pricing, etc.

This means:
- Remove `position: fixed` from `.map-container`, `.map-overlay`, `.search-float`
- Add `.hero-viewport { height: 100vh; position: relative; overflow: hidden; }`
- Map, overlay, search card become `position: absolute` inside `.hero-viewport`
- All new sections are standard `position: static` block elements below

## Header Navigation

Current header: `MapSearch [logo]` ... `EN | 99 credits | theme | Sign In`

Add nav links after logo: **Features | Pricing | How it works**

These are anchor links (`#features`, `#pricing`, `#how-it-works`) with smooth scroll behavior. Header remains `position: fixed` so nav links are always accessible.

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
| Starter | 1,000 | $1.50 | $1.50 | "Buy" → auth gate then Stripe |
| Growth | 5,000 | $7.00 | $1.40 | "Buy" → auth gate then Stripe |
| Pro | 25,000 | $32.00 | $1.28 | "Buy" → auth gate then Stripe |
| Agency | 100,000 | $120.00 | $1.20 | "Buy" → auth gate then Stripe |

Growth card gets a "Popular" badge.

### Pricing auth gate

Buy buttons use the same `Auth.showModal(callback)` pattern as the search flow:

```javascript
function buyPack(packId) {
    const user = State.get('user');
    if (!user) {
        Auth.showModal(() => buyPack(packId));
        return;
    }
    Credits.purchase(packId);
}
```

This is a new inline function in the pricing section's `<script>` block or added to `credits.js`. It wraps `Credits.purchase()` with the auth check, reusing the existing modal callback pattern.

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
Button: "Sign up for free" → opens signup modal via `Auth.showModal()`

## Section 5: Footer

Minimal footer:
- Left: "© 2026 MapSearch"
- No language selector in footer (it's already in the fixed header, visible at all times)

## Technical Notes

### Files to modify
- `app/templates/app.html` — restructure into hero-viewport wrapper + add all sections
- `app/static/css/app.css` — hero-viewport styles, section styles (port from `design/html/landing.html`), update map/overlay/search-float from fixed to absolute
- `app/static/js/credits.js` — add `buyPack(packId)` auth-gate wrapper
- `app/static/i18n/en.json`, `fr.json`, `de.json`, `es.json` — add translation keys for all new section text

### Files NOT to create
- No new routes. No new JS files (credits.js gets the auth-gate wrapper).

### Smooth scroll
Add `scroll-behavior: smooth` to `html` element. Nav links use standard `<a href="#features">`.

### Mobile
- Feature cards: 1 column on mobile, 2 on tablet, 3 on desktop
- Pricing cards: 1 column on mobile, scrollable horizontal on tablet, 5 across on desktop
- How it works: stack vertically on mobile
- Header nav items: hide on mobile (sections are scrollable, and the fixed header is narrow on mobile)

### i18n
All new text uses `data-i18n` attributes. Translation keys MUST be added to all 4 JSON files (en, fr, de, es) as part of this implementation — not deferred. The fallback text in HTML serves as the English default; the JSON files provide the actual translations.

### Design reference
Port styles from `design/html/landing.html` where applicable (section spacing, pricing cards, step cards). Adapt to match the existing app.css design system (accent colors, glass effects, dark theme).
