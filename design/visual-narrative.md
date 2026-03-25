# MapSearch.app — Visual Narrative Specification

---

## 1. The First 10 Seconds

The landing page IS the product. No splash screen, no hero image, no scrolling needed. The user lands inside the app.

| Second | What the user sees | What they feel | What they do |
|--------|-------------------|----------------|--------------|
| 0-1 | Full-screen dark map fades in. Muted tiles, soft glow at center. The world, waiting. | "This is different." Unexpected. Intriguing. | Eyes scan the screen. |
| 1-2 | A floating search bar materializes center-top with a gentle slide-down + fade. Placeholder text types itself: `Search any area. Get every business.` | Recognition — this is a search tool. But gorgeous. | Mouse moves toward the search bar. |
| 2-3 | Subtle pin cluster animates in the background — 30-40 ghost pins scatter across the visible map area, then fade to 15% opacity. A visual promise: "data lives here." | "There's something here already." Curiosity builds. | Eyes track the pins, then return to search bar. |
| 3-5 | The headline below the search bar fades in: **"Find every business in any area. Filter. Export. Done."** Below it, three micro-stats slide up one by one: `99 free credits` / `Results in seconds` / `Free CSV export` | Clarity — they understand what this does. The free credits register. | They start typing a keyword or city. |
| 5-8 | As they type, the map smoothly pans/zooms to the location. Autocomplete suggestions appear in a clean dropdown. Filter chips appear below the search bar (subtle, not overwhelming). | "This is fast. This is smart." Confidence grows. | They select a location, maybe toggle a filter. |
| 8-10 | They hit Search. If logged in: results stream in. If not: a clean modal slides up — "Create your free account. 99 credits included." Google sign-in button prominent. | The friction is minimal. 99 free credits feels generous. | They sign up (10 seconds) or scroll down to learn more. |

**Design principle:** The product sells itself. The first 10 seconds are a guided tour disguised as a landing page.

---

## 2. Emotional Journey Map

```
SKEPTICAL ──────> CURIOUS ──────> IMPRESSED ──────> CONVINCED ──────> SIGNED UP
   │                 │                 │                  │                │
   │                 │                 │                  │                │
"Another SaaS    "Wait, this      "This actually    "It's cheaper    "99 free
 tool? I've       looks like a      works. And        AND better       credits?
 seen plenty."    real product."    it's beautiful."  than what I      Let me
                                                      use now."        try it."
```

### Emotional Triggers by Section

| Section | Emotion triggered | Mechanism |
|---------|-------------------|-----------|
| Hero (map + search bar) | **Curiosity** | The map is unexpected. Most SaaS tools have a stock photo hero. This IS the product. |
| Ghost pins animation | **Intrigue** | Data is already here. This isn't vaporware — it's alive. |
| First search (or demo) | **Delight** | Speed. Results in seconds, not minutes. Beautiful table, not a CSV dump. |
| Filter panel | **Empowerment** | "I can find exactly what I need." Every toggle feels precise. |
| Pricing section | **Relief** | No subscriptions. No enterprise sales calls. Credits start at $1.50/1,000. |
| Outscraper comparison | **Validation** | "I'm making the smart choice." Data proves it. |
| Signup modal | **Confidence** | 99 free credits. Google one-click. No credit card. Zero risk. |

---

## 3. Hero Section Design Spec

### Layout (Desktop 1440px)

```
┌──────────────────────────────────────────────────────────────────┐
│  [Logo]  MapSearch                    [EN|FR|ES|DE]  [Sign In]  │  <- Nav: frosted glass, fixed
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│                         FULL-SCREEN MAP                          │
│                     (dark/muted Leaflet tiles)                   │
│                                                                  │
│              ┌─────────────────────────────────────┐             │
│              │  🔍  Dentists in Zürich       [Search]│            │  <- Search bar: floating, centered
│              └─────────────────────────────────────┘             │
│                                                                  │
│              ┌── Filter chips (collapsed) ──────────┐            │
│              │ Has website ▾  Rating ▾  Email ▾  +3 │            │
│              └──────────────────────────────────────┘            │
│                                                                  │
│          "Find every business in any area."                      │  <- Value prop: large, centered
│           Filter. Export. Done.                                   │
│                                                                  │
│         ┌──────────┐  ┌──────────┐  ┌──────────────┐            │
│         │ 99 free  │  │ Results  │  │ Free CSV     │            │  <- Micro-stats: three pills
│         │ credits  │  │ in secs  │  │ export       │            │
│         └──────────┘  └──────────┘  └──────────────┘            │
│                                                                  │
│                  ·  ·  ·  ghost pins  ·  ·  ·                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Map Background

- **Tile source:** OpenStreetMap via Leaflet.js, using CartoDB Dark Matter or Stadia Dark tiles
- **Opacity:** Map at 100%, but tiles are inherently muted (dark theme, desaturated labels)
- **Interaction:** Fully interactive — drag, zoom, click to set location
- **Initial view:** Europe centered (or geolocated if permission granted), zoom level 5
- **Ghost pins:** 20-30 semi-transparent pins (8% opacity) scattered across visible area, purely decorative, removed on first real search

### Search Bar

- **Width:** 560px max, 90vw on mobile
- **Height:** 56px (generous touch target)
- **Background:** White with subtle shadow (`0 4px 24px rgba(0,0,0,0.12)`)
- **Border-radius:** 12px
- **Layout:** Search icon (left) + dual input (keyword | location) + Search button (right, accent color)
- **States:** Default (placeholder typing animation) / Focused (subtle glow ring) / Loading (button becomes spinner)

### Value Proposition

- **Headline:** `font-size: 2rem`, `font-weight: 700`, white text, text-shadow for map contrast
- **Subheadline:** `font-size: 1.125rem`, `font-weight: 400`, white at 80% opacity
- **Position:** Centered below search bar, 32px gap
- **Background:** No box. Text reads directly over the dark map. Text shadow provides contrast.

### Micro-Stats Pills

- **Layout:** Horizontal row, centered, 16px gap
- **Each pill:** Frosted glass background (`backdrop-filter: blur(12px)`, `background: rgba(255,255,255,0.08)`), `border-radius: 8px`, `padding: 8px 16px`
- **Text:** `font-size: 0.875rem`, white, medium weight
- **Animation:** Slide up with stagger (100ms delay each), fade in

---

## 4. How It Works — 3 Steps

### Section Design

Clean white/dark section below the hero. Three columns on desktop, stacked on mobile. Each step has an icon, number, title, and one-line description.

### Step 1: Search

- **Icon:** Magnifying glass over a map pin (or a stylized map with a search bar)
- **Visual:** Screenshot/mockup of the search bar with a keyword typed and the map zoomed to a city
- **Title:** "Search any area"
- **Description:** "Type a keyword and pick a location. Set filters for exactly what you need — websites, emails, ratings, and more."
- **Color accent:** Step number "1" in the primary accent color, large (48px), semi-transparent behind the icon

### Step 2: Discover

- **Icon:** Table/grid icon with data rows, or a list with checkmarks
- **Visual:** Screenshot/mockup of the results table with map pins visible in the background
- **Title:** "Get instant results"
- **Description:** "Results appear in seconds — not hours. A filterable table with every detail, plus pins on the map for geographic context."
- **Color accent:** Step number "2"

### Step 3: Export

- **Icon:** Download arrow into a document, or CSV file icon
- **Visual:** Screenshot/mockup of the export button with a "618 results — Download CSV" label
- **Title:** "Export and use"
- **Description:** "Download your data as a clean CSV. Free export — no extra charge. Your data, your way."
- **Color accent:** Step number "3"

### Layout Spec

```
Desktop (1024px+):
┌─────────────────────────────────────────────────────────────┐
│                     How It Works                             │
│                                                              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐       │
│  │     (1)      │   │     (2)      │   │     (3)      │      │
│  │  [icon]      │   │  [icon]      │   │  [icon]      │      │
│  │  Search any  │   │  Get instant │   │  Export      │      │
│  │  area        │   │  results     │   │  and use     │      │
│  │              │   │              │   │              │      │
│  │  description │   │  description │   │  description │      │
│  └─────────────┘   └─────────────┘   └─────────────┘       │
│                                                              │
│           ──── connecting line or arrow ────                 │
└─────────────────────────────────────────────────────────────┘

Mobile:
  Vertical stack, each step full-width, 48px gap between.
  Step numbers align left, content indented.
```

---

## 5. Social Proof Strategy (No Testimonials)

Since we're launching fresh with zero customers, we use **data-driven trust signals** instead of testimonials.

### What We Show

| Signal | Value | Visual Treatment | Why It Works |
|--------|-------|------------------|--------------|
| **Free credits** | "99 free credits on signup" | Prominent badge, repeated in hero + pricing + signup modal | Generosity signals confidence in the product |
| **Data freshness** | "Google Maps data, updated daily" | Small text near search bar | Establishes data quality without claiming our own track record |
| **Coverage stat** | "200M+ businesses indexed worldwide" | Large number in the "How It Works" section | Scale = trust (this is Google's data via DataForSEO) |
| **Speed claim** | "Results in under 5 seconds" | Animated counter near search bar or in stats section | Measurable, verifiable on first use |
| **Language count** | "Available in 4 languages" | Language flags in footer and nav | Professionalism, global product |
| **Export freedom** | "Free CSV export — no extra charges" | Highlighted in pricing section | Differentiator, signals fairness |
| **No subscription** | "Pay as you go. No monthly fees." | Pricing section headline | Removes commitment anxiety |
| **Comparison data** | "$1.50 vs $3.00 per 1,000 results" | Subtle comparison table in pricing | Let the numbers speak |

### Trust Layout (Between "How It Works" and Pricing)

```
┌──────────────────────────────────────────────────┐
│                                                   │
│   200M+              <5 sec            4            │
│   businesses         average           languages   │
│   indexed            response                      │
│                                                   │
│   Free export     No subscription    99 free      │
│   included        required           credits      │
│                                                   │
└──────────────────────────────────────────────────┘
```

- **Design:** Six items in a 3x2 grid (desktop) or 2x3 (tablet) or single column (mobile)
- **Each item:** Large number/keyword in accent color, small descriptor below in muted text
- **Background:** Subtle gradient or section divider to separate from surrounding content

### Future Social Proof (Post-Launch)

- Real-time counter: "12,847 searches today" (once we have volume)
- Logos of customer segments (not specific companies): "Trusted by marketing agencies, direct mail companies, and freelancers"
- G2/Capterra badges (when available)

---

## 6. Pricing Display Design

### Section Layout

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                   │
│         Pay as you go. No subscriptions.                          │
│         1 credit = 1 business result                              │
│                                                                   │
│  ┌──────────┐ ┌──────────┐ ┌───────────┐ ┌───────────┐          │
│  │  FREE    │ │ STARTER  │ │  GROWTH   │ │   PRO     │          │
│  │          │ │          │ │ POPULAR   │ │           │          │
│  │ 99       │ │ 1,000    │ │ 5,000     │ │ 25,000    │          │
│  │ credits  │ │ credits  │ │ credits   │ │ credits   │          │
│  │          │ │          │ │           │ │           │          │
│  │  $0      │ │  $1.50   │ │   $7      │ │   $32     │          │
│  │          │ │          │ │           │ │           │          │
│  │ $0/result│ │$1.50/1k  │ │ $1.40/1k  │ │ $1.28/1k  │          │
│  │          │ │          │ │           │ │           │          │
│  │[Sign up] │ │  [Buy]   │ │   [Buy]   │ │   [Buy]   │          │
│  │  free    │ │          │ │           │ │           │          │
│  └──────────┘ └──────────┘ └───────────┘ └───────────┘          │
│                                                                   │
│  Need more? Agency pack: 100,000 credits for $120 ($1.20/1k)    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐     │
│  │  How does MapSearch compare?                             │     │
│  │                                                          │     │
│  │  For $7, you get:                                        │     │
│  │  MapSearch:  5,000 results + map view + free export      │     │
│  │  Others:     ~2,300 results, CSV only, no map            │     │
│  │                                                          │     │
│  │  "Same data. Half the price. 10x the experience."        │     │
│  └─────────────────────────────────────────────────────────┘     │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Card Design

- **Card size:** Equal width, ~260px each on desktop
- **Popular badge:** "POPULAR" pill on Growth card, accent color background
- **Price:** Large font (2.5rem), bold, primary color
- **Per-result math:** Small text below price, muted: "$1.40 per 1,000 results"
- **CTA button:** Full-width within card. Free = outline style. Paid = filled accent color.
- **Hover:** Subtle lift (translateY -2px) + shadow increase

### Outscraper Comparison

- **Tone:** Factual, not aggressive. Never name "Outscraper" — say "other tools" or "typical competitors"
- **Format:** Simple inline comparison, not a full comparison table (that feels desperate)
- **Key points:** 2x more results per dollar, free export included, instant results (not queued), interactive map view
- **Design:** Muted background card below pricing cards, smaller text, feels like a footnote — discoverable but not pushy

---

## 7. Micro-Interactions List

Every interactive moment in the application, designed to feel responsive, polished, and purposeful.

### Navigation & Global

| Element | Trigger | Animation | Purpose |
|---------|---------|-----------|---------|
| Page load | DOMContentLoaded | Map fades in (300ms ease-out), then search bar slides down (400ms, 100ms delay) | Sets the stage, prevents layout shift |
| Nav bar | Scroll past hero | Background transitions from transparent to frosted glass (200ms) | Context shift — user is now browsing content |
| Language selector | Click | Dropdown slides down (150ms), flag icons scale in | Quick, non-disruptive language switch |
| Credit balance | Credit change | Number counts up/down (odometer style, 600ms) | Makes credit usage feel tangible and trackable |
| Dark/light toggle | Click | Smooth color transition on all elements (300ms) | Respects user preference without jarring flash |

### Search Flow

| Element | Trigger | Animation | Purpose |
|---------|---------|-----------|---------|
| Search bar placeholder | Page load | Text types itself letter by letter (50ms/char): "Search any area. Get every business." | Draws attention, communicates purpose |
| Keyword input | Focus | Border glow ring (accent color, 200ms), placeholder fades out | Clear focus state |
| Location autocomplete | Typing (debounced 300ms) | Dropdown slides down with suggestions (150ms), each item fades in with 30ms stagger | Fast, responsive, no layout jump |
| Map pan to location | Location selected | Smooth flyTo animation (1.5s ease-in-out) with zoom adjustment | Geographic context, satisfying movement |
| Filter chips | Click to expand | Chip expands to reveal filter controls (200ms slide), other chips shift (150ms) | Progressive disclosure, no overwhelm |
| Filter toggle (Yes/No/Any) | Click | Segment control slides active indicator (150ms) | Immediate feedback on selection |
| Rating slider | Drag | Track fills with accent color, tooltip follows thumb showing value | Precision control with visual feedback |
| Search button | Hover | Subtle scale (1.02) + shadow increase (150ms) | Affordance — this is clickable |
| Search button | Click | Button contracts slightly (scale 0.97, 100ms), then loading spinner replaces text | Immediate feedback that action was registered |
| Results loading | Search submitted | Skeleton rows shimmer in the table area (pulse animation), map pins appear as dots first | Perceived speed — something is happening |
| Results delivery | Data loaded | Table rows slide in from bottom with 20ms stagger per row, map pins drop in | Satisfying reveal, data feels alive |

### Results Table

| Element | Trigger | Animation | Purpose |
|---------|---------|-----------|---------|
| Table row | Hover | Background highlight (50ms), corresponding map pin pulses | Table-map connection |
| Map pin | Hover | Pin scales up (1.3x, 150ms), info tooltip appears | Geographic context for a data point |
| Map pin | Click | Pin bounces, corresponding table row highlights and scrolls into view | Bidirectional linking |
| Column header | Click | Sort arrow rotates (200ms), rows re-sort with subtle slide (300ms) | Clear sort direction feedback |
| Column header | Hover | Subtle background tint + cursor change | Affordance — sortable |
| Filter count | Filter change | Number morphs (old fades out, new fades in, 200ms): "Showing 234 of 618 results" | Immediate feedback on filter impact |
| Pagination | Page change | Current page rows fade out (150ms), new rows fade in (150ms) | Smooth transition, no jarring reload |
| CSV export button | Click | Button shows progress (determinate bar fills), then check icon replaces text (300ms) | Feedback that download is preparing |
| Empty state | No results match filters | Illustration fades in with "No results match your filters. Try adjusting." | Friendly, not a dead end |

### Signup Modal

| Element | Trigger | Animation | Purpose |
|---------|---------|-----------|---------|
| Modal | Search without account | Backdrop fades in (200ms), modal slides up from bottom (300ms, spring ease) | Non-jarring interruption |
| Google sign-in button | Hover | Subtle lift + shadow | Primary action affordance |
| Email/password fields | Focus | Label floats up (200ms), border accent | Material-style input feedback |
| Form submission | Click | Button loading state, then success check or error shake | Clear success/failure feedback |
| Modal close | Click backdrop/X | Modal slides down (200ms), backdrop fades out (150ms) | Clean exit |
| Success state | Account created | Modal content morphs: form fades out, welcome message + credit balance fades in, confetti subtle | Celebration moment — they just got 99 free credits |

### Credit Purchase

| Element | Trigger | Animation | Purpose |
|---------|---------|-----------|---------|
| Pricing card | Hover | Lift (translateY -4px) + shadow increase (200ms) | Card is interactive |
| Popular badge | Idle | Subtle pulse every 3s (scale 1.0 -> 1.05 -> 1.0) | Draws eye to recommended option |
| Buy button | Click | Transitions to Stripe checkout (loading overlay with spinner) | Trust — Stripe handles payment |
| Credit balance | Purchase complete | Number counts up (odometer, 800ms), brief glow effect on balance | Satisfying confirmation of purchase |

### Scroll-Based

| Element | Trigger | Animation | Purpose |
|---------|---------|-----------|---------|
| "How It Works" steps | Scroll into view | Each step fades in + slides up with 200ms stagger | Progressive reveal as user reads down |
| Stats numbers | Scroll into view | Numbers count up from 0 (1.2s, ease-out) | Makes numbers feel dynamic and real |
| Pricing cards | Scroll into view | Cards scale in from 0.95 to 1.0 with 100ms stagger | Gentle entrance, not distracting |
| Comparison section | Scroll into view | Fade in (400ms) | Subtle, since this is supplementary content |

---

## Design Tokens Reference

These micro-interactions reference timing and easing values. Standardize them:

| Token | Value | Usage |
|-------|-------|-------|
| `--duration-fast` | 150ms | Hovers, toggles, small state changes |
| `--duration-normal` | 300ms | Modal open/close, section reveals |
| `--duration-slow` | 600ms | Map animations, number counters |
| `--ease-default` | cubic-bezier(0.4, 0, 0.2, 1) | Most transitions (Material Design standard) |
| `--ease-spring` | cubic-bezier(0.34, 1.56, 0.64, 1) | Modal entrance, pin bounce |
| `--ease-out` | cubic-bezier(0, 0, 0.2, 1) | Exit animations |
