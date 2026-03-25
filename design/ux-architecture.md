# MapSearch.app — UX Architecture

Version: 1.0.0
Last updated: 2026-03-24

---

## 1. Information Architecture

### Page Hierarchy

```
mapsearch.app/
├── /                          Landing (full-screen map + floating search)
├── /results?q=...&loc=...     Results (table + map split view)
├── /account                   Account settings (profile, language)
├── /credits                   Credit balance + purchase
├── /history                   Search history (v1.1)
├── /login                     Login (redirects to / after auth)
├── /signup                    Signup (redirects to / after account creation)
├── /terms                     Terms of service
├── /privacy                   Privacy policy
└── /api/...                   Backend endpoints (not navigable)
```

### Navigation Structure

**Header (persistent, all pages):**

```
┌──────────────────────────────────────────────────────────────────┐
│  [Logo] MapSearch           [Credits: 47]  [EN ▾]  [◐]  [User] │
└──────────────────────────────────────────────────────────────────┘
```

| Element | Behavior | Visibility |
|---------|----------|------------|
| Logo | Links to `/` | Always |
| Credits pill | Shows remaining credits; links to `/credits` | Logged in |
| Language selector | Dropdown: EN/FR/ES/DE; saves to profile | Always |
| Theme toggle | Cycles: light -> dark -> system; persists in localStorage | Always |
| User avatar/menu | Dropdown: Account, History, Logout | Logged in |
| Login button | Links to signup modal | Logged out |

**No sidebar navigation.** The app is two pages (landing + results) with modals for auth and credits. Minimal chrome, maximum content.

---

## 2. User Flow Diagrams

### Primary Flow: First-time user to export

```
                        ┌─────────┐
                        │  LAND   │
                        │  (map)  │
                        └────┬────┘
                             │
                      type keyword
                      set location
                             │
                        ┌────▼────┐
                        │ FILTERS │ (optional)
                        │ expand  │
                        └────┬────┘
                             │
                        hit Search
                             │
                    ┌────────▼────────┐
           no ◄────┤  Logged in?     ├────► yes
           │       └─────────────────┘       │
      ┌────▼────┐                            │
      │ SIGNUP  │                            │
      │ MODAL   │                            │
      │ (OAuth  │                            │
      │  or     │                            │
      │ email)  │                            │
      └────┬────┘                            │
           │ +99 credits                     │
           └──────────────┬──────────────────┘
                          │
                   ┌──────▼──────┐
            no ◄───┤  Enough     ├───► yes
            │      │  credits?   │       │
       ┌────▼────┐ └─────────────┘  ┌────▼────┐
       │ CREDITS │                  │ SEARCH  │
       │ PURCHASE│                  │ (API)   │
       │ MODAL   │                  └────┬────┘
       └────┬────┘                       │
            │ + credits             credits deducted
            └────────────┬───────────────┘
                         │
                    ┌────▼────┐
                    │ RESULTS │
                    │ (table  │
                    │  + map) │
                    └────┬────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
         ┌────▼───┐ ┌───▼────┐ ┌───▼───┐
         │ SORT   │ │ FILTER │ │EXPORT │
         │columns │ │(client)│ │ (CSV) │
         └────────┘ └────────┘ └───────┘
```

### Theme Toggle Flow

```
    Click toggle
         │
    ┌────▼──────────────────────┐
    │  Current theme?           │
    │                           │
    │  light ──► dark           │
    │  dark  ──► system         │
    │  system──► light          │
    └────┬──────────────────────┘
         │
    Set data-theme on <html>
    Save to localStorage
         │
    ┌────▼──────────────────────┐
    │  If "system":             │
    │  Read prefers-color-scheme│
    │  Apply matching palette   │
    └───────────────────────────┘
```

### Map + Table Interaction

```
    ┌─────────────────┐         ┌─────────────────┐
    │     TABLE        │         │      MAP         │
    │                  │         │                  │
    │  hover row  ─────┼────────►│  highlight pin   │
    │                  │         │                  │
    │  ◄───────────────┼─────────  hover pin        │
    │  highlight row   │         │                  │
    │                  │         │                  │
    │  click row  ─────┼────────►│  pan to pin +    │
    │                  │         │  open popup      │
    │                  │         │                  │
    │  ◄───────────────┼─────────  click pin        │
    │  scroll to row + │         │                  │
    │  highlight       │         │                  │
    └─────────────────┘         └─────────────────┘
```

---

## 3. Responsive Strategy

### Breakpoints

| Token | Width | Target |
|-------|-------|--------|
| base | 0-639px | Phones (portrait) |
| sm | 640-767px | Phones (landscape), small tablets |
| md | 768-1023px | Tablets |
| lg | 1024-1279px | Small laptops, tablets landscape |
| xl | 1280px+ | Desktops |

### Section Adaptation Table

| Section | base (320px) | sm (640px) | md (768px) | lg (1024px) | xl (1280px) |
|---------|-------------|-----------|-----------|------------|------------|
| **Header** | Logo + credits + hamburger (48px tall) | + language selector | + theme toggle | Full nav (56px tall) | Full nav |
| **Landing map** | Full viewport, map behind search | Same | Same | Same | Same |
| **Search card** | Full width with 16px margins, stacked inputs | Side-by-side keyword + location | Wider card (600px) | 680px max card | Same |
| **Filter panel** | 1-col grid in expanding section | 2-col grid | 3-col grid | 4-col grid | Same |
| **Results toolbar** | Count + export button only | + view toggle | + filter sidebar trigger | Full toolbar | Same |
| **Results body** | Table only (full width), no map | Same | Same | Split: table + 400px map | Split: table + 480px map |
| **Data table** | Horizontal scroll, 6 visible cols | 7 cols | 8 cols | All default cols | All cols, comfortable widths |
| **Table columns** | Name, Category, City, Phone, Rating, Reviews | + Website | + Email | All always-visible | Same |
| **Filter sidebar** | Slide-in from left (85vw max) with backdrop | Same | Same | Same | Same |
| **Modal (signup)** | Nearly full screen (96vw) | Centered 440px max | Same | Same | Same |
| **Credit cards** | 1-col stack | 2-col grid | Same | Same | Same |
| **Footer** | Stacked: links then copyright | Single row | Same | Same | Same |
| **Map pins** | Hidden (no map on mobile) | Hidden | Map-only view available | Visible in split view | Same |
| **View toggle** | Hidden (table-only forced) | Hidden | Show (table/map) | Show (table/split/map) | Same |

### Key Responsive Decisions

1. **Table is ALWAYS available.** The map is the luxury that gets cut first. Users come for data, not geography.
2. **Horizontal scroll on mobile tables is acceptable.** The table has 8+ columns; forcing them into cards would destroy scannability. The Airtable pattern (horizontal scroll with sticky first column) works.
3. **Filter sidebar is an overlay on all breakpoints.** Not inline. This keeps the results area clean and doesn't cause layout shifts.
4. **Search card is responsive via CSS grid, not JS.** Inputs stack on mobile, go side-by-side on sm+.
5. **The map in split view has a fixed width** (400-480px), not a percentage. The table gets all remaining space. This prevents the map from being too small to be useful.

---

## 4. Keyboard Navigation Plan

### Global Shortcuts

| Key | Action | Context |
|-----|--------|---------|
| `/` | Focus search keyword input | Landing page |
| `Escape` | Close modal, close filter sidebar, clear selection | Any |
| `Tab` / `Shift+Tab` | Standard focus traversal | All interactive elements |

### Search Card

| Key | Action |
|-----|--------|
| `Enter` (in keyword input) | Move focus to location input |
| `Enter` (in location input) | Submit search |
| `Tab` from location | Focus "Filters" toggle |
| `Enter`/`Space` on Filters toggle | Expand/collapse filter panel |
| `Tab` within filters | Traverse filter controls |
| `Escape` in filters | Collapse filter panel, return focus to toggle |

### Data Table

| Key | Action |
|-----|--------|
| `Tab` | Move to next focusable cell (links, buttons) |
| `Arrow Up/Down` | Move row highlight (when table has focus) |
| `Enter` on row | Open pin popup on map (if split view) |
| `Home` | Jump to first row |
| `End` | Jump to last row |
| Click column header | Sort ascending; click again for descending; third click clears sort |

### Modal

| Key | Action |
|-----|--------|
| `Escape` | Close modal |
| `Tab` | Cycle through modal controls (trapped focus) |
| `Shift+Tab` | Reverse cycle |
| `Enter` on primary button | Submit form |

### Focus Management Rules

1. **Opening a modal:** Focus moves to the modal's first focusable element (close button or first input). Focus is trapped inside the modal.
2. **Closing a modal:** Focus returns to the element that triggered the modal.
3. **Opening filter sidebar:** Focus moves to the sidebar's close button.
4. **Closing filter sidebar:** Focus returns to the filter trigger button.
5. **After search completes:** Focus moves to the results count text (announced by screen reader via `aria-live`).
6. **All custom controls** (theme toggle, view toggle, filter toggle) use `role`, `aria-pressed`, `aria-expanded` as appropriate.

### ARIA Patterns Used

| Component | ARIA Pattern |
|-----------|-------------|
| Theme toggle | `role="button"`, `aria-pressed`, `aria-label="Toggle theme"` |
| View toggle buttons | `role="radio"` inside `role="radiogroup"`, `aria-pressed` |
| Filter toggle | `aria-expanded`, `aria-controls="filter-panel"` |
| Filter sidebar | `role="dialog"`, `aria-label="Filters"`, `aria-modal="true"` |
| Signup modal | `role="dialog"`, `aria-labelledby`, `aria-modal="true"` |
| Sort headers | `aria-sort="ascending|descending|none"` |
| Results count | `aria-live="polite"` region |
| Loading state | `aria-busy="true"` on results container |
| Credit balance | `aria-live="polite"` (updates when credits change) |

---

## 5. Theme Toggle Specification

### HTML

```html
<!-- In header -->
<button
  class="theme-toggle"
  id="theme-toggle"
  type="button"
  role="button"
  aria-label="Toggle theme"
  aria-pressed="false"
  title="Toggle theme"
>
  <!-- Sun icon (shown in dark mode) -->
  <svg class="theme-toggle__icon theme-toggle__icon--light" aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="5"/>
    <line x1="12" y1="1" x2="12" y2="3"/>
    <line x1="12" y1="21" x2="12" y2="23"/>
    <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
    <line x1="1" y1="12" x2="3" y2="12"/>
    <line x1="21" y1="12" x2="23" y2="12"/>
    <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
    <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
  </svg>
  <!-- Moon icon (shown in light mode) -->
  <svg class="theme-toggle__icon theme-toggle__icon--dark" aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
  </svg>
  <!-- Monitor icon (shown in system mode) -->
  <svg class="theme-toggle__icon theme-toggle__icon--system" aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
    <line x1="8" y1="21" x2="16" y2="21"/>
    <line x1="12" y1="17" x2="12" y2="21"/>
  </svg>
</button>
```

### CSS (icon visibility)

```css
/* Only show the icon for the NEXT theme in the cycle */
/* light mode -> show moon (clicking goes to dark) */
[data-theme="light"] .theme-toggle__icon--light,
[data-theme="light"] .theme-toggle__icon--system { display: none; }

/* dark mode -> show monitor (clicking goes to system) */
[data-theme="dark"] .theme-toggle__icon--dark,
[data-theme="dark"] .theme-toggle__icon--light { display: none; }

/* system mode -> show sun (clicking goes to light) */
[data-theme="system"] .theme-toggle__icon--system,
[data-theme="system"] .theme-toggle__icon--dark { display: none; }
```

### JavaScript

```javascript
/**
 * Theme toggle controller.
 *
 * Cycle: light -> dark -> system -> light
 * Persists choice in localStorage('mapsearch-theme').
 * On page load, reads stored preference or defaults to 'system'.
 */
(function () {
  'use strict';

  var STORAGE_KEY = 'mapsearch-theme';
  var CYCLE = ['light', 'dark', 'system'];
  var html = document.documentElement;
  var toggle = document.getElementById('theme-toggle');

  function getStoredTheme() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (e) {
      return null;
    }
  }

  function setTheme(theme) {
    html.setAttribute('data-theme', theme);
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (e) {
      // localStorage unavailable — theme still works via attribute
    }
    // Update aria-label to indicate current state
    if (toggle) {
      var labels = {
        light: 'Theme: light. Click for dark.',
        dark: 'Theme: dark. Click for system.',
        system: 'Theme: system. Click for light.'
      };
      toggle.setAttribute('aria-label', labels[theme] || 'Toggle theme');
    }
  }

  // Initialize on page load (runs before paint if script is in <head>)
  var stored = getStoredTheme();
  var initial = (stored && CYCLE.indexOf(stored) !== -1) ? stored : 'system';
  setTheme(initial);

  // Toggle handler
  if (toggle) {
    toggle.addEventListener('click', function () {
      var current = html.getAttribute('data-theme') || 'system';
      var idx = CYCLE.indexOf(current);
      var next = CYCLE[(idx + 1) % CYCLE.length];
      setTheme(next);
    });
  }
})();
```

### Inline `<head>` Script (Flash Prevention)

Place this in `<head>` before any stylesheet to prevent FOUC on page load:

```html
<script>
(function(){var t;try{t=localStorage.getItem('mapsearch-theme')}catch(e){}
if(t&&['light','dark','system'].indexOf(t)!==-1){document.documentElement.setAttribute('data-theme',t)}
else{document.documentElement.setAttribute('data-theme','system')}})();
</script>
```

---

## 6. Layout Decisions & Rationale

### Decision 1: Table-first, map-secondary

**Choice:** On all breakpoints, the data table is the primary interface. The map provides geographic context but is not required.

**Rationale:** Users come to MapSearch to get business data for export. The table is where they scan, sort, filter, and select. The map helps them confirm geographic coverage but is not the workflow center. On mobile (where screen space is scarce), cutting the map loses almost no functionality.

### Decision 2: Floating search card over full-screen map

**Choice:** The landing page is a full-viewport map with a floating search card centered near the top.

**Rationale:** The map IS the brand. It communicates "this is a geographic search tool" instantly. The floating card creates a clean, focused entry point. This pattern (Google Maps, Airbnb) is immediately recognizable. The map is interactive behind the card — users can pan and zoom to set their location before typing.

### Decision 3: Filter sidebar as overlay, not inline

**Choice:** Post-search filters open as a slide-in sidebar over the results, not as an inline panel that shifts the layout.

**Rationale:** Inline filter panels cause content shifts and waste space when open. An overlay keeps the results table at full width at all times. The sidebar opens on demand and closes when done. This matches the Airtable and Linear pattern of "filters are transient, results are persistent."

### Decision 4: Fixed-width map pane in split view

**Choice:** The map pane in split view is 400px (lg) or 480px (xl) fixed width. The table gets all remaining space.

**Rationale:** A percentage-based split (e.g., 50/50) makes the table too narrow on smaller screens and gives the map too much space. The map only needs enough width to show pins in context. The table needs as much width as possible for 8+ columns. A fixed map width guarantees both are usable.

### Decision 5: Pre-search filter expansion, not separate page

**Choice:** Filters expand below the search card on the landing page (before search), not on a separate page or step.

**Rationale:** Progressive disclosure. Most users will search with just keyword + location. Power users can expand filters without leaving the search context. No page transition, no lost state. The expansion is animated to feel smooth and intentional.

### Decision 6: Signup wall at search time, not on landing

**Choice:** Users can explore the map, set location, type keyword, and configure filters without an account. The signup wall appears only when they hit "Search."

**Rationale:** Let users invest effort before asking for commitment. By the time they've typed a keyword and set a location, they've committed intent. The signup wall converts better because they're one step from results, not zero steps in.

### Decision 7: Credits always visible in header

**Choice:** Credit balance is permanently displayed in the header as a pill/badge.

**Rationale:** Credits are the currency of the app. Users need constant awareness of their balance to feel in control. Hiding it behind a menu creates anxiety ("how many do I have left?"). The pill format is compact and unobtrusive while always being visible. It also serves as a link to the purchase page, making the buy flow one click away.

### Decision 8: Dark map tiles on landing, standard tiles in results

**Choice:** Landing page uses muted/dark map tiles (CartoDB Dark Matter or similar). Results page uses standard OpenStreetMap tiles.

**Rationale:** The landing page is a brand moment — dark tiles create a premium, modern feel and let the UI elements (search card, pins) pop. The results page is a work environment — standard tiles provide better readability for geographic context when users are analyzing data.

### Decision 9: No pagination, virtual scroll for large result sets

**Choice:** Results table uses virtual scrolling (render only visible rows) rather than pagination.

**Rationale:** Pagination breaks flow. Users want to scroll through results fluidly, especially when scanning for patterns ("which businesses have no website?"). Virtual scroll handles 700 rows (the DataForSEO max) without performance issues. The table header stays sticky for context.

### Decision 10: CSV export is free, instant, client-side

**Choice:** CSV export downloads the currently filtered/sorted table data. No server round-trip, no additional credits.

**Rationale:** The data is already in the browser (loaded after search). Generating CSV client-side is instant. Charging for export would be a dark pattern since the user already paid for the search. Free export is a competitive advantage over Outscraper.
