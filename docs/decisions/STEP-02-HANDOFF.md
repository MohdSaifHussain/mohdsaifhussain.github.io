# HANDOFF — mohdsaifhussain.github.io · "Ledger Amber" (direction 1b/2a, final)
Deliverable per DESIGN_BRIEF.md. Designs live in `Home Explorations.dc.html` — turn 2 (Home, final) + turn 3 (Projects 3a, Experience 3b, Certifications 3c, /audit 3d). Charter (SITE_CHARTER.md v1.0) wins every conflict. **No logos anywhere — all employers/issuers typographic (owner-confirmed).**

## 1 · Tokens

### Color (all vs bg #0d0d0c, contrast noted)
| token | value | use | contrast |
|---|---|---|---|
| bg | #0d0d0c | page background | — |
| ink | #f2f0eb | display text, strong rules | 15.9:1 |
| body | #cfccc3 | body/receipt text | 10.6:1 |
| bright | #e8e5dd | evidence text | 13.6:1 |
| dim | #8f8c83 | metadata, labels | 5.1:1 (small caps labels only) |
| accent | #e8b64c | ONE accent: numerals, ✓, links, current-nav | 9.3:1 |
| rule-strong | #f2f0eb @ 2px | section-opening ledger rule | — |
| rule-mid | rgba(242,240,235,.4) @ 1px | row separators | — |
| rule-faint | rgba(242,240,235,.25) @ 1px | dense table rows (/audit) | — |

### Type (two faces, self-host: Instrument Serif 400 + italic; IBM Plex Mono 400/500/600)
| step | spec | use |
|---|---|---|
| display-xl | Serif 400 62/1.14, ls −0.005em | Home identity line |
| display-lg | Serif 400 54/1 | page h1 |
| display-md | Serif 400 40/1.05 | project name (slider) |
| display-sm | Serif 400 36/1.05 · 24/1.15 | row titles |
| numeral | Serif 400 44/1 accent | entry numbers "01" |
| wordmark-nav | Serif 400 17/1, ls +0.22em, caps | nav |
| wordmark-foot | Serif 400 13/1, ls +0.22em, caps, dim | footer |
| quote | Serif italic 17 or 15/1.5, body color | problem statements |
| mono-body | Mono 400 12.5–13/1.6 | receipts, method |
| mono-meta | Mono 400 11–11.5/1.6, dim | metadata strips |
| mono-label | Mono 600 10/1, ls +0.12em, caps | section labels "02 / 04 — …" |
| mono-link | Mono 600 11/1, accent | REPO ↗ etc. |
Minimum text size 10px labels / 11px meta; body ≥12.5px.

### Spacing / layout
Page gutter 48px · section pad-top 56–72px · row pad 24–26px 0 · grid gap 28px (24 in tables) · card pad 34×38px. Wordmark rule system: 2px ink opens a section, 1px mid separates rows, 2px ink closes a table.

## 2 · Motif
Verification mark (✓ accent / ✗ dim) + ledger rule. Every claim row carries ✓ or an honest ✗ ("pending owner verification"). Numbered everything: nav items 01–04 + A, sections "01 / 04", entries "01 / 05".

## 3 · Page layouts
- **Home** (2a): nav → identity (mono label + serif identity line with amber italic clause + double-rule headline strip) → flagship ledger (2 rows, grid 120/1fr/1fr/220) → truth strip → footer.
- **Projects** (3a): h1 "Case ledger" + "05 ENTRIES · SCROLL →"; horizontal CSS scroll-snap slider (`scroll-snap-type:x mandatory`, cards 1100px, `scroll-snap-align:start`, native visible scrollbar); card = number/status → name → problem quote → METHOD | VERIFIED METRICS grid → rule + links.
- **Experience** (3b): h1 "Nine years, receipted" + PDF button (1px accent border, inverts on hover); table NO./PERIOD/ROLE/RECEIPTS (60/200/1fr/1.35fr), 6 rows, education line after close-rule.
- **Certifications** (3c): count "00 ENTRIES · VERIFIED ONLY"; empty state centered: "00 / 00" + serif italic "Entries appear as completed — verified only." + policy note; tile-anatomy specimen (dashed border, NOT A CLAIM) + 2 empty dashed slots. 3-col tile grid when populated.
- **/audit** (3d): tables A1 STANDARDS (target vs measured; unmeasured = "— AT DEPLOY", CI-written, never hand-entered), A2 CHARTER CHECKS, A3 SHIPPED ANIMATIONS; live-values line.
- **Footer everywhere**: wordmark-foot · LINKEDIN ↗ GITHUB ↗ · VISITS (real counter or "—") · colophon line → /audit.
- **Truth strip**: live IST clock (accent ● + HH:MM:SS IST, JS 1s tick, `Intl` Asia/Kolkata) · HYDERABAD, IN · real counts (delivery-engine 419 / analystkit 53 / opskit 18 / 8 TOML). Test counts refresh at build (C-35).

## 4 · Component specs
- **Project card (Home flagship row)**: grid 120/1fr/1fr/220; evidence layer = absolutely positioned over name+problem columns ONLY (left:148px; right:248px), `background:#0d0d0c`, `pointer-events:none`, `opacity:0→1 200ms ease`, driven by row `mouseenter/mouseleave` (JS state, no descendant CSS). Links column NEVER covered — interaction-QA rule is mandatory on every future component.
- **Badge tile**: 1px border (dashed = specimen, solid = real entry), pad 26px, min-height 200px; NO./status row → serif course name 26/1.15 → issuer (typographic) / completed YYYY-MM / VERIFY CREDENTIAL ↗. Only entries with real verification URL or honest no-public-verification flag.
- **Slider**: native scroll-snap only; no JS carousel, no arrows required; position visible via scrollbar + numbered cards.
- **Audit table**: mono 12/1.5 rows on rule-faint separators; measured column uses ✓ + value or dim "— AT DEPLOY".
- **Nav**: wordmark left; right mono links `01 INDEX … A / AUDIT`; current page = accent + 1px accent underline + ✓. Always visible; any page ≤2 interactions.

## 5 · Animations (complete list — nothing else ships)
| # | animation | props | duration | answers |
|---|---|---|---|---|
| A3.1 | Home evidence reveal (pointer-events:none layer) | opacity | 200ms | WHAT JUST HAPPENED |
| A3.2 | Projects slider — native scroll-snap | native scroll | — | WHERE AM I |
| A3.3 | Link/nav hover color swap (instant, no transition) | color | 0ms | WHAT CAN I DO |
Reduced-motion: kill the 200ms transition; all states remain reachable and coherent.

## 6 · Build notes for Claude Code
- Self-host both fonts (woff2, `font-display:swap` is banned if it costs a Lighthouse point — subset + preload instead). No third-party assets, trackers, cookies, analytics beyond a privacy-safe visit counter. No email/phone. Photo unused in committed direction (owner call at review was pure-type 1b); files exist in uploads/ if reinstated.
- All stats render from JSON (profile/projects/experience/certifications.json); test counts + versions fetched at build (C-35); "— AT DEPLOY" scores written by CI.
- TS-Sentry metrics: render honest ✗ pending until owner supplies.
- Targets: Lighthouse 100×4 · WCAG 2.2 AA, axe 0 · W3C 0 errors · body contrast ≥4.5:1 (achieved ≥10:1).
- Interaction QA (frozen project rule): no animation/overlay may block or overlap any interactive element in any state.
