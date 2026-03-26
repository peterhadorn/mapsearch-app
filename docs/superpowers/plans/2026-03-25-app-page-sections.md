# App Page Sections Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Features, Pricing, How it works, CTA, and Footer sections below the existing map hero on the MapSearch single-page app, with header navigation that smooth-scrolls to each section.

**Architecture:** Restructure the current `position: fixed` layout into a hero-viewport wrapper (100vh) with scrollable sections below. All changes are HTML + CSS in `app.html` and `app.css`, plus a small JS addition to `credits.js` for the pricing auth gate. Styles ported from the existing `design/html/landing.html` prototype.

**Tech Stack:** Jinja2 template, vanilla CSS, existing JS modules (State, Auth, Credits)

**Spec:** `docs/superpowers/specs/2026-03-25-app-page-sections-design.md`

---

## File Structure

```
Modified files:
├── app/templates/app.html          # Hero wrapper + 5 new sections + header nav
├── app/static/css/app.css          # Hero viewport, section styles, responsive
├── app/static/js/credits.js        # buyPack() auth-gate wrapper
├── app/templates/base.html         # Cache bust version bump
├── app/static/i18n/en.json         # New translation keys
├── app/static/i18n/fr.json         # French translations
├── app/static/i18n/de.json         # German translations
├── app/static/i18n/es.json         # Spanish translations
```

No new files created. No new routes. No new JS modules.

---

## Task 1: Hero Viewport Restructure

**Files:**
- Modify: `app/templates/app.html`
- Modify: `app/static/css/app.css`

This is the critical structural change. The current map, overlay, and search card are `position: fixed`. They need to become `position: absolute` inside a `100vh` wrapper so sections can flow below.

- [ ] **Step 1: Add hero-viewport wrapper in app.html**

Wrap the map, overlay, search card, and results panel inside a `<div class="hero-viewport">` — place it right after the header, before the map div. Close it after the results panel div (line 286). The signup modal stays OUTSIDE the wrapper (it's a fixed overlay).

```html
  <!-- after header (line 59) -->

  <!-- ================================================================
       HERO VIEWPORT — 100vh wrapper for map + search
       ================================================================ -->
  <div class="hero-viewport" id="hero">

    <!-- existing map, overlay, search-float, results-panel go here unchanged -->

  </div><!-- end hero-viewport -->

  <!-- signup modal stays here, outside hero-viewport -->
```

- [ ] **Step 2: Add hero-viewport CSS**

Add to `app.css` before the `#map` rule (around line 235):

```css
/* ================================================================
   Hero viewport — contains the fixed-like map + search as 100vh block
   ================================================================ */
.hero-viewport {
  position: relative;
  height: 100vh;
  overflow: hidden;
}
```

- [ ] **Step 3: Change map, overlay, search-float from fixed to absolute**

In `app.css`:

`#map` (line ~239): change `position: fixed` → `position: absolute`

`.map-overlay` (line ~246): change `position: fixed` → `position: absolute`

`.search-float` (line ~268): change `position: fixed` → `position: absolute`

`.results-panel` (line ~740): change `position: fixed` → `position: absolute`

The header (`position: fixed`) stays unchanged — it floats above everything.

- [ ] **Step 4: Add smooth scroll to html**

Add at the top of `app.css` (or in the base reset section):

```css
html {
  scroll-behavior: smooth;
}
```

- [ ] **Step 5: Verify the hero still looks correct**

Deploy and check that the map, overlay, search card, and filters all render correctly at 100vh. The page should now be scrollable (even though there's nothing below yet — the body extends past 100vh because of the wrapper).

Run: `./deploy.sh app`

- [ ] **Step 6: Commit**

```bash
git add app/templates/app.html app/static/css/app.css
git commit -m "refactor: hero-viewport wrapper — fixed to absolute positioning for scrollable sections"
```

---

## Task 2: Header Navigation

**Files:**
- Modify: `app/templates/app.html`
- Modify: `app/static/css/app.css`

- [ ] **Step 1: Add nav links to header in app.html**

After the logo link (line 17), before `<div class="header__actions">` (line 19), add a nav element:

```html
    <nav class="header__nav hide-mobile">
      <a href="#features" class="header__nav-link" data-i18n="nav_features">Features</a>
      <a href="#pricing" class="header__nav-link" data-i18n="nav_pricing">Pricing</a>
      <a href="#how-it-works" class="header__nav-link" data-i18n="nav_how">How it works</a>
    </nav>
```

- [ ] **Step 2: Add header nav CSS**

```css
.header__nav {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-left: var(--space-6);
}
.header__nav-link {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 200ms;
}
.header__nav-link:hover {
  color: var(--text-primary);
}
```

- [ ] **Step 3: Commit**

```bash
git add app/templates/app.html app/static/css/app.css
git commit -m "feat: header nav links — Features, Pricing, How it works"
```

---

## Task 3: Features Section

**Files:**
- Modify: `app/templates/app.html`
- Modify: `app/static/css/app.css`

- [ ] **Step 1: Add features section HTML**

Add after the hero-viewport closing `</div>` and before the signup modal, in `app.html`:

```html
  <!-- ================================================================
       FEATURES
       ================================================================ -->
  <section class="page-section" id="features">
    <div class="section-inner">
      <p class="section-label" data-i18n="features.label">Features</p>
      <h2 class="section-title" data-i18n="features.title">Everything you need to find businesses at scale</h2>

      <!-- Block 1: Tool capabilities -->
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-card__icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          </div>
          <h3 class="feature-card__title" data-i18n="features.realtime_title">Real-time results</h3>
          <p class="feature-card__desc" data-i18n="features.realtime_desc">Results in seconds, not hours. No task queues, no waiting.</p>
        </div>
        <div class="feature-card">
          <div class="feature-card__icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>
          </div>
          <h3 class="feature-card__title" data-i18n="features.filters_title">10+ filters</h3>
          <p class="feature-card__desc" data-i18n="features.filters_desc">Website, email, phone, rating, reviews, claimed, photos, price, category. Pay only for what passes.</p>
        </div>
        <div class="feature-card">
          <div class="feature-card__icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          </div>
          <h3 class="feature-card__title" data-i18n="features.export_title">CSV export</h3>
          <p class="feature-card__desc" data-i18n="features.export_desc">Download your results as CSV. Free with every search.</p>
        </div>
        <div class="feature-card">
          <div class="feature-card__icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
          </div>
          <h3 class="feature-card__title" data-i18n="features.map_title">Interactive map</h3>
          <p class="feature-card__desc" data-i18n="features.map_desc">See every result on a live map. Click pins, hover rows.</p>
        </div>
        <div class="feature-card">
          <div class="feature-card__icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
          </div>
          <h3 class="feature-card__title" data-i18n="features.langs_title">4 languages</h3>
          <p class="feature-card__desc" data-i18n="features.langs_desc">EN, FR, DE, ES. Auto-detects your browser language.</p>
        </div>
        <div class="feature-card">
          <div class="feature-card__icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          </div>
          <h3 class="feature-card__title" data-i18n="features.cache_title">Smart cache</h3>
          <p class="feature-card__desc" data-i18n="features.cache_desc">Same search within 72h costs zero extra credits.</p>
        </div>
      </div>

      <!-- Block 2: Data fields (pills are technical field names — no i18n needed) -->
      <h3 class="section-subtitle" data-i18n="features.data_title">40+ data points per business</h3>
      <div class="data-pills">
        <span class="data-pill">Business name</span>
        <span class="data-pill">Category</span>
        <span class="data-pill">Address</span>
        <span class="data-pill">City</span>
        <span class="data-pill">State</span>
        <span class="data-pill">ZIP</span>
        <span class="data-pill">Country</span>
        <span class="data-pill">Phone</span>
        <span class="data-pill">Email</span>
        <span class="data-pill">Domain</span>
        <span class="data-pill">URL</span>
        <span class="data-pill">Rating</span>
        <span class="data-pill">Reviews</span>
        <span class="data-pill">Claimed</span>
        <span class="data-pill">Verified</span>
        <span class="data-pill">Photos</span>
        <span class="data-pill">Main image</span>
        <span class="data-pill">Latitude</span>
        <span class="data-pill">Longitude</span>
        <span class="data-pill">Google Maps URL</span>
        <span class="data-pill">Price level</span>
        <span class="data-pill">Work hours</span>
        <span class="data-pill">Business status</span>
        <span class="data-pill">Rating distribution</span>
        <span class="data-pill">Additional categories</span>
        <span class="data-pill">Place ID</span>
        <span class="data-pill">CID</span>
      </div>

      <!-- Block 3: Why MapSearch -->
      <h3 class="section-subtitle" data-i18n="features.why_title">Same data. Half the price. Better experience.</h3>
      <div class="why-grid">
        <div class="why-card">
          <strong data-i18n="features.why_cheaper">2x cheaper</strong>
          <span data-i18n="features.why_cheaper_desc">$1.50/1,000 vs Outscraper's $3/1,000</span>
        </div>
        <div class="why-card">
          <strong data-i18n="features.why_instant">Instant results</strong>
          <span data-i18n="features.why_instant_desc">Real-time API, not async task queues</span>
        </div>
        <div class="why-card">
          <strong data-i18n="features.why_noapi">No API keys</strong>
          <span data-i18n="features.why_noapi_desc">Just sign up and search. No developer setup.</span>
        </div>
        <div class="why-card">
          <strong data-i18n="features.why_filters">Filters save money</strong>
          <span data-i18n="features.why_filters_desc">618 raw results → 234 with email → pay for 234</span>
        </div>
      </div>
    </div>
  </section>
```

- [ ] **Step 2: Add features CSS**

```css
/* ================================================================
   Page sections — shared styles
   ================================================================ */
.page-section {
  padding: 80px 24px;
  background: var(--surface-primary);
  border-top: 1px solid var(--border-secondary);
}
[data-theme="dark"] .page-section {
  background: #0c0d0f;
}
.section-inner {
  max-width: 1100px;
  margin: 0 auto;
}
.section-label {
  font-size: 0.8125rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--accent-500);
  margin-bottom: 8px;
}
.section-title {
  font-size: clamp(1.5rem, 3vw, 2.25rem);
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: -0.02em;
  margin-bottom: 16px;
  color: var(--text-primary);
}
.section-subtitle {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 48px 0 20px;
}

/* Feature cards grid */
.features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-top: 32px;
}
@media (max-width: 767px) {
  .features-grid { grid-template-columns: 1fr; }
}
@media (min-width: 768px) and (max-width: 1023px) {
  .features-grid { grid-template-columns: repeat(2, 1fr); }
}
.feature-card {
  background: var(--surface-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  padding: 24px;
  transition: transform 200ms, box-shadow 200ms;
}
.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.15);
}
.feature-card__icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-500);
  margin-bottom: 12px;
}
.feature-card__icon svg { width: 24px; height: 24px; }
.feature-card__title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 6px;
}
.feature-card__desc {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* Data field pills */
.data-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}
.data-pill {
  padding: 6px 14px;
  background: var(--surface-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: 100px;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

/* Why MapSearch comparison cards */
.why-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
@media (max-width: 639px) {
  .why-grid { grid-template-columns: 1fr; }
}
.why-card {
  background: var(--surface-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.why-card strong {
  font-size: 1rem;
  color: var(--accent-500);
}
.why-card span {
  font-size: 0.875rem;
  color: var(--text-secondary);
}
```

- [ ] **Step 3: Deploy and verify**

Run: `./deploy.sh app`
Check: scroll below the map hero → Features section visible with 6 cards, data pills, and why-cards

- [ ] **Step 4: Commit**

```bash
git add app/templates/app.html app/static/css/app.css
git commit -m "feat: features section — tool capabilities, data fields, comparison"
```

---

## Task 4: Pricing Section

**Files:**
- Modify: `app/templates/app.html`
- Modify: `app/static/css/app.css`
- Modify: `app/static/js/credits.js`

- [ ] **Step 1: Add pricing section HTML**

Add after the features section in `app.html`:

```html
  <!-- ================================================================
       PRICING
       ================================================================ -->
  <section class="page-section" id="pricing">
    <div class="section-inner section-center">
      <p class="section-label" data-i18n="pricing.label">Pricing</p>
      <h2 class="section-title" data-i18n="pricing.title">Pay as you go. No subscriptions.</h2>
      <p class="section-desc" data-i18n="pricing.subtitle">1 credit = 1 filtered result. Filters save you money.</p>

      <div class="pricing-grid">
        <div class="pricing-card">
          <div class="pricing-name" data-i18n="pricing.free_name">Free</div>
          <div class="pricing-credits">99 <small data-i18n="pricing.credits_label">credits</small></div>
          <div class="pricing-price pricing-price--free" data-i18n="pricing.free_price">$0</div>
          <div class="pricing-per" data-i18n="pricing.free_per">On signup</div>
          <button class="btn--pricing" onclick="Auth.showModal()" data-i18n="pricing.get_started">Get started</button>
        </div>
        <div class="pricing-card">
          <div class="pricing-name" data-i18n="pricing.starter_name">Starter</div>
          <div class="pricing-credits">1,000 <small data-i18n="pricing.credits_label">credits</small></div>
          <div class="pricing-price">$1.50</div>
          <div class="pricing-per">$1.50 / 1,000</div>
          <button class="btn--pricing" onclick="Credits.buyPack('starter')" data-i18n="pricing.buy">Buy</button>
        </div>
        <div class="pricing-card popular">
          <div class="popular-badge" data-i18n="pricing.popular">Popular</div>
          <div class="pricing-name" data-i18n="pricing.growth_name">Growth</div>
          <div class="pricing-credits">5,000 <small data-i18n="pricing.credits_label">credits</small></div>
          <div class="pricing-price">$7.00</div>
          <div class="pricing-per">$1.40 / 1,000</div>
          <button class="btn--pricing" onclick="Credits.buyPack('growth')" data-i18n="pricing.buy">Buy</button>
        </div>
        <div class="pricing-card">
          <div class="pricing-name" data-i18n="pricing.pro_name">Pro</div>
          <div class="pricing-credits">25,000 <small data-i18n="pricing.credits_label">credits</small></div>
          <div class="pricing-price">$32</div>
          <div class="pricing-per">$1.28 / 1,000</div>
          <button class="btn--pricing" onclick="Credits.buyPack('pro')" data-i18n="pricing.buy">Buy</button>
        </div>
        <div class="pricing-card">
          <div class="pricing-name" data-i18n="pricing.agency_name">Agency</div>
          <div class="pricing-credits">100,000 <small data-i18n="pricing.credits_label">credits</small></div>
          <div class="pricing-price">$120</div>
          <div class="pricing-per">$1.20 / 1,000</div>
          <button class="btn--pricing" onclick="Credits.buyPack('agency')" data-i18n="pricing.buy">Buy</button>
        </div>
      </div>
    </div>
  </section>
```

- [ ] **Step 2: Add buyPack auth gate to credits.js**

Add this method to the `Credits` object literal in `app/static/js/credits.js` (same level as `purchase`, `showModal`, etc.):

```javascript
    buyPack(packId) {
        const user = State.get('user');
        if (!user) {
            Auth.showModal(() => Credits.buyPack(packId));
            return;
        }
        this.purchase(packId);
    },
```

- [ ] **Step 3: Add pricing CSS**

Port and adapt from `design/html/landing.html` (lines 582-704):

```css
/* Pricing section */
.section-center { text-align: center; }
.section-desc {
  font-size: 1.0625rem;
  color: var(--text-secondary);
  max-width: 560px;
  margin: 0 auto 40px;
}
.pricing-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
  margin-top: 32px;
}
@media (max-width: 1023px) {
  .pricing-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 639px) {
  .pricing-grid { grid-template-columns: 1fr; }
}
.pricing-card {
  background: var(--surface-elevated);
  border: 1px solid var(--border-secondary);
  border-radius: var(--radius-lg);
  padding: 28px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
  transition: transform 200ms, box-shadow 200ms;
  position: relative;
}
.pricing-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.2);
}
.pricing-card.popular {
  border-color: var(--accent-500);
  box-shadow: 0 0 0 1px var(--accent-500), 0 8px 24px rgba(16, 185, 129, 0.15);
}
.popular-badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--accent-500);
  color: #fff;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 4px 14px;
  border-radius: 100px;
}
.pricing-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.pricing-credits {
  font-size: 1.75rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}
.pricing-credits small {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary);
}
.pricing-price {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent-500);
}
.pricing-price--free {
  color: var(--accent-400);
}
.pricing-per {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  font-variant-numeric: tabular-nums;
}
.btn--pricing {
  margin-top: 12px;
  width: 100%;
  padding: 10px 0;
  background: var(--accent-500);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 200ms;
}
.btn--pricing:hover {
  background: var(--accent-400);
}
```

- [ ] **Step 4: Deploy and verify**

Run: `./deploy.sh app`
Check: scroll to Pricing → 5 cards, Growth has "Popular" badge. Click "Buy" while logged out → signup modal appears.

- [ ] **Step 5: Commit**

```bash
git add app/templates/app.html app/static/css/app.css app/static/js/credits.js
git commit -m "feat: pricing section with 5 credit packs + auth-gated buy buttons"
```

---

## Task 5: How It Works + CTA + Footer

**Files:**
- Modify: `app/templates/app.html`
- Modify: `app/static/css/app.css`

- [ ] **Step 1: Add how-it-works, CTA, and footer HTML**

Add after the pricing section in `app.html`:

```html
  <!-- ================================================================
       HOW IT WORKS
       ================================================================ -->
  <section class="page-section" id="how-it-works">
    <div class="section-inner section-center">
      <p class="section-label" data-i18n="how.label">How it works</p>
      <h2 class="section-title" data-i18n="how.title">Three steps. That's it.</h2>
      <p class="section-desc" data-i18n="how.subtitle">No API keys. No task queues. No waiting.</p>

      <div class="steps-grid">
        <div class="step-card">
          <div class="step-number">1</div>
          <div class="step-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
          </div>
          <h3 class="step-title" data-i18n="how.step1_title">Search</h3>
          <p class="step-desc" data-i18n="how.step1_desc">Enter a keyword and location. We search Google Maps in real time.</p>
        </div>
        <div class="step-card">
          <div class="step-number">2</div>
          <div class="step-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/><line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/><line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/><line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="17" y1="16" x2="23" y2="16"/></svg>
          </div>
          <h3 class="step-title" data-i18n="how.step2_title">Filter</h3>
          <p class="step-desc" data-i18n="how.step2_desc">Narrow results with 10+ filters. Only pay for what passes.</p>
        </div>
        <div class="step-card">
          <div class="step-number">3</div>
          <div class="step-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          </div>
          <h3 class="step-title" data-i18n="how.step3_title">Export</h3>
          <p class="step-desc" data-i18n="how.step3_desc">Download CSV or browse the interactive table + map.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- ================================================================
       CTA
       ================================================================ -->
  <section class="cta-section">
    <h2 class="cta-title" data-i18n="cta.title">Ready to find every business in your area?</h2>
    <p class="cta-desc" data-i18n="cta.desc">99 free credits. No credit card required.</p>
    <button class="btn--cta" onclick="Auth.showModal()" data-i18n="cta.button">Sign up for free</button>
  </section>

  <!-- ================================================================
       FOOTER
       ================================================================ -->
  <footer class="site-footer">
    <span>&copy; 2026 MapSearch</span>
  </footer>
```

- [ ] **Step 2: Add how-it-works, CTA, footer CSS**

```css
/* Steps grid */
.steps-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  margin-top: 32px;
}
@media (max-width: 767px) {
  .steps-grid { grid-template-columns: 1fr; gap: 24px; }
}
.step-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;
}
.step-number {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-elevated);
  border: 2px solid var(--accent-500);
  border-radius: 50%;
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--accent-500);
}
.step-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-500);
}
.step-icon svg { width: 28px; height: 28px; }
.step-title { font-size: 1.125rem; font-weight: 700; }
.step-desc { font-size: 0.9375rem; color: var(--text-secondary); line-height: 1.6; max-width: 280px; }

/* CTA section */
.cta-section {
  padding: 80px 24px;
  text-align: center;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(139, 92, 246, 0.08));
  border-top: 1px solid var(--border-secondary);
}
.cta-title {
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 800;
  margin-bottom: 12px;
}
.cta-desc {
  font-size: 1.0625rem;
  color: var(--text-secondary);
  margin-bottom: 28px;
}
.btn--cta {
  padding: 14px 36px;
  background: var(--accent-500);
  color: #fff;
  border: none;
  border-radius: var(--radius-lg);
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 200ms, transform 200ms;
}
.btn--cta:hover {
  background: var(--accent-400);
  transform: translateY(-2px);
}

/* Footer */
.site-footer {
  padding: 24px;
  text-align: center;
  font-size: 0.8125rem;
  color: var(--text-tertiary);
  border-top: 1px solid var(--border-secondary);
}
```

- [ ] **Step 3: Deploy and verify**

Run: `./deploy.sh app`
Check: scroll through all sections — Features → Pricing → How it works → CTA → Footer. CTA button opens signup modal.

- [ ] **Step 4: Commit**

```bash
git add app/templates/app.html app/static/css/app.css
git commit -m "feat: how it works, CTA, footer sections"
```

---

## Task 6: i18n Translation Keys

**Files:**
- Modify: `app/static/i18n/en.json`
- Modify: `app/static/i18n/fr.json`
- Modify: `app/static/i18n/de.json`
- Modify: `app/static/i18n/es.json`

- [ ] **Step 1: Add English translation keys**

Add these keys to `en.json` (nested under appropriate sections):

```json
{
  "nav_features": "Features",
  "nav_pricing": "Pricing",
  "nav_how": "How it works",

  "features": {
    "label": "Features",
    "title": "Everything you need to find businesses at scale",
    "realtime_title": "Real-time results",
    "realtime_desc": "Results in seconds, not hours. No task queues, no waiting.",
    "filters_title": "10+ filters",
    "filters_desc": "Website, email, phone, rating, reviews, claimed, photos, price, category. Pay only for what passes.",
    "export_title": "CSV export",
    "export_desc": "Download your results as CSV. Free with every search.",
    "map_title": "Interactive map",
    "map_desc": "See every result on a live map. Click pins, hover rows.",
    "langs_title": "4 languages",
    "langs_desc": "EN, FR, DE, ES. Auto-detects your browser language.",
    "cache_title": "Smart cache",
    "cache_desc": "Same search within 72h costs zero extra credits.",
    "data_title": "40+ data points per business",
    "why_title": "Same data. Half the price. Better experience.",
    "why_cheaper": "2x cheaper",
    "why_cheaper_desc": "$1.50/1,000 vs Outscraper's $3/1,000",
    "why_instant": "Instant results",
    "why_instant_desc": "Real-time API, not async task queues",
    "why_noapi": "No API keys",
    "why_noapi_desc": "Just sign up and search. No developer setup.",
    "why_filters": "Filters save money",
    "why_filters_desc": "618 raw results → 234 with email → pay for 234"
  },

  "pricing": {
    "label": "Pricing",
    "title": "Pay as you go. No subscriptions.",
    "subtitle": "1 credit = 1 filtered result. Filters save you money.",
    "credits_label": "credits",
    "free_name": "Free",
    "free_price": "$0",
    "free_per": "On signup",
    "starter_name": "Starter",
    "growth_name": "Growth",
    "pro_name": "Pro",
    "agency_name": "Agency",
    "popular": "Popular",
    "get_started": "Get started",
    "buy": "Buy"
  },

  "how": {
    "label": "How it works",
    "title": "Three steps. That's it.",
    "subtitle": "No API keys. No task queues. No waiting.",
    "step1_title": "Search",
    "step1_desc": "Enter a keyword and location. We search Google Maps in real time.",
    "step2_title": "Filter",
    "step2_desc": "Narrow results with 10+ filters. Only pay for what passes.",
    "step3_title": "Export",
    "step3_desc": "Download CSV or browse the interactive table + map."
  },

  "cta": {
    "title": "Ready to find every business in your area?",
    "desc": "99 free credits. No credit card required.",
    "button": "Sign up for free"
  }
}
```

- [ ] **Step 2: Add French translations to fr.json**

Use the same key structure. Translate all values to French. The implementor should produce natural French copy (not machine-translated word-for-word). Key examples:
- `features.title` → "Tout ce qu'il faut pour trouver des entreprises à grande échelle"
- `pricing.title` → "Payez à l'utilisation. Sans abonnement."
- `how.title` → "Trois étapes. C'est tout."
- `cta.title` → "Prêt à trouver chaque entreprise dans votre zone ?"

- [ ] **Step 3: Add German translations to de.json**

Key examples:
- `features.title` → "Alles was Sie brauchen, um Unternehmen in grossem Stil zu finden"
- `pricing.title` → "Bezahlen Sie nach Verbrauch. Kein Abo."
- `how.title` → "Drei Schritte. Das war's."
- `cta.title` → "Bereit, jedes Unternehmen in Ihrer Gegend zu finden?"

- [ ] **Step 4: Add Spanish translations to es.json**

Key examples:
- `features.title` → "Todo lo que necesitas para encontrar negocios a escala"
- `pricing.title` → "Paga por uso. Sin suscripciones."
- `how.title` → "Tres pasos. Eso es todo."
- `cta.title` → "¿Listo para encontrar cada negocio en tu zona?"

- [ ] **Step 5: Bump cache version in base.html**

Change all `?v=5` to `?v=6` in `app/templates/base.html`.

- [ ] **Step 6: Deploy and verify**

Run: `./deploy.sh app`
Check: change language selector → all section text translates correctly in all 4 languages.

- [ ] **Step 7: Commit**

```bash
git add app/static/i18n/ app/templates/base.html
git commit -m "feat: i18n translations for all new sections (EN/FR/DE/ES)"
```

---

## Summary

| Task | What | Files |
|------|------|-------|
| 1 | Hero viewport restructure | app.html, app.css |
| 2 | Header navigation | app.html, app.css |
| 3 | Features section (3 blocks) | app.html, app.css |
| 4 | Pricing section + auth gate | app.html, app.css, credits.js |
| 5 | How it works + CTA + Footer | app.html, app.css |
| 6 | i18n translations (4 languages) | en/fr/de/es.json, base.html |

**Total: 6 tasks. No tests needed (HTML/CSS only, existing tests still pass).**

**Dependencies:** Task 1 first (structural), then 2-5 in any order, Task 6 last (needs all section text finalized).
