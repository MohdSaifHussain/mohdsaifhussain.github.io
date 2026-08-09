# Motion Spec — v1.1 "Signature Motion"

**Status:** FINAL · Design session closed by owner ruling 2026-08-10
**Applies to:** https://mohdsaifhussain.github.io/ (Ledger Amber, v1.0.0)
**Governs:** the Claude Code build under existing gates (`check_animations.py` updated two-directionally in the same commit as the first new animation)
**Ruling:** M-1 accepted (vertical ledger-turn, 250ms, site-wide). M-2 accepted (Experience register only; Home and Projects excluded as decoration). M-3 STRUCK as pre-registered — no interactive surface is non-redundant (nav has M-1; links have A3.3 plus the navigation itself) and every other surface would be a false affordance. Selection rule satisfied: 2 of 3. A3 ledger grows 4 → 6 entries.

---

## A3.5 — Cross-document view transition, vertical ledger-turn (M-1)

**Question it answers (C-12):** WHERE AM I — the wordmark and nav never leave the page, so navigation is continuity of place, never a "new site" moment.

**Scope:** site-wide; every same-origin navigation between the five pages.

**Mechanism:** native CSS cross-document View Transitions. Zero JS, zero bytes of library (C-19). Opt in on every page:

```css
@view-transition { navigation: auto; }
```

**Elements involved:**

| Element | `view-transition-name` | Behaviour |
|---|---|---|
| `header` (wordmark + nav + rule) | `site-header` | Persists — snapshotted as its own group; geometry identical on all five pages, so it holds still. The `nav-link--current` marker (accent + check mark) changes with the incoming DOM, instantly — it is state, not motion. |
| `footer` | `site-footer` | Persists — identical on all five pages, holds still. |
| `main` | `page-content` | Transitions: old content turns out, new content turns in. |

**Properties (transform / opacity only, C-15):**

```css
::view-transition-old(page-content) {
  animation: vt-turn-out 250ms cubic-bezier(.22,.61,.36,1) both;
}
::view-transition-new(page-content) {
  animation: vt-turn-in 250ms cubic-bezier(.22,.61,.36,1) both;
}
@keyframes vt-turn-out { to   { opacity: 0; transform: translateY(-16px); } }
@keyframes vt-turn-in  { from { opacity: 0; transform: translateY(22px); } }
```

**Duration:** 250ms (owner ruling; between the compared 200/350 candidates), driven by one token so the lever below reaches it:

```css
:root { --motion-vt: 250ms; }
```

and `var(--motion-vt)` in both `animation` declarations. Within C-15's ≤400ms transition cap.

**Easing:** `cubic-bezier(.22,.61,.36,1)` (ease-out) on both old and new, as demoed (canvas option 1c/1d lineage, at the ruled 250ms).

**Reduced motion (C-10 — the single lever):** the existing tokens.css block zeroes the token:

```css
@media (prefers-reduced-motion: reduce) { :root { --motion-vt: 0ms; } }
```

At 0ms the pseudo-elements resolve instantly: navigation is an instant swap, every state reachable and coherent. Design note per the brief: the lever's definition widens from "one variable" to "one mechanism — zeroed motion tokens" (`--motion-reveal` + `--motion-vt`); record as a design note citing C-10, not a charter amendment.

**Degraded behaviour (no `@view-transition` support):** the at-rule is ignored; navigation is completely normal, content always visible, nothing delayed or hidden. True progressive enhancement — no `@supports` wrapper needed, and the transition never blocks the swap (the P3.2 counsel's recorded distinction).

**Guarantees:** no overlay covers any interactive element in any state — `::view-transition` pseudo-elements exist only during the ~250ms swap and the header/footer groups sit over their own static geometry; LCP unaffected (first load has no transition; C-02's 1.65s cannot regress from a navigation-time crossfade); CLS 0.000 (no geometry change — transforms only).

---

## A3.6 — Scroll-driven reveal, Experience register (M-2)

**Question it answers (C-12):** WHERE AM I — rows and their rules surface in step with their arrival at the reading edge, and scrub back on upward scroll, so the reveal frontier IS the reader's position in the six-role register.

**Scope:** `/experience/` receipts table ONLY — `.xp-row` and `.receipt-rule` inside `.section--table`. Home and Projects excluded as decoration (owner ruling, per the one-sentence test). The page `h1`, `.pdf-button`, `.xp-head` and anything above the fold never participate.

**Mechanism:** CSS `animation-timeline: view()` — no JS, no scroll listeners, no library (C-19).

**Properties (transform / opacity only, C-15):**

```css
@supports (animation-timeline: view()) {
  .xp-row {
    animation: xp-surface auto linear both;
    animation-timeline: view();
    animation-range: entry 10% entry 55%;
  }
  .receipt-rule {
    animation: xp-rule auto linear both;
    animation-timeline: view();
    animation-range: entry 15% entry 70%;
    transform-origin: left center;
  }
}
@keyframes xp-surface { from { opacity: 0; transform: translateY(12px); } }
@keyframes xp-rule    { from { transform: scaleX(0); } }
```

**Duration / easing:** scrubbed, not timed — progress is bound to scroll position (`linear` against the view timeline), so C-15's time caps do not bind; no frame can exceed the reader's own scroll speed. The micro-interaction envelope is respected by construction.

**LCP / CLS guarantees:** elements already inside the viewport at first paint are past their `entry` range and render at final state — nothing above the fold ever starts hidden (C-02, zero headroom at 1.65s). Transforms and opacity only: CLS 0.000.

**Reduced motion (C-10 — the single lever):**

```css
@media (prefers-reduced-motion: reduce) {
  .xp-row, .receipt-rule { animation: none; }
}
```

Everything static and visible from first paint; the register is complete and coherent.

**Degraded behaviour (no `animation-timeline` support):** the `@supports` wrapper means non-supporting browsers never see the `from` states — every row and rule visible, statically, from first paint. Content is never hidden behind an API the browser lacks (C-10 applied to feature detection, per the reviewed brief).

**Interaction with A3.4:** compatible, not redundant — A3.4 is the hover/focus reading tint (instant, background/colour); A3.6 is arrival at the reading edge (scroll-scrubbed, transform/opacity). Neither covers nor delays the other; `.xp-row:hover` works identically mid-range.

---

## A3 ledger entries (declaration schema, for /audit and check_animations.py)

| No. | Element(s) | Properties | Duration | Question |
|---|---|---|---|---|
| A3.5 | `::view-transition-old/new(page-content)`; `header`/`footer` persist via `view-transition-name` | transform, opacity | 250ms, cubic-bezier(.22,.61,.36,1) | WHERE AM I |
| A3.6 | `.xp-row`, `.receipt-rule` (/experience/ only) | transform, opacity | scroll-scrubbed (`view()`), linear | WHERE AM I |

Undeclared motion remains a defect. M-3 recorded as STRUCK in `docs/decisions/` with the reasoning from the design session's 1f verdict card.
