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

---

# Errata

Recorded against this specification after the build ran it. **The specification
text above is left intact as the historical record** — same convention as
Erratum 1 against STEP-02-HANDOFF (defect D-34). An erratum records that the
artifact and the spec disagree and says which one is right; it does not quietly
rewrite the spec so the disagreement disappears.

## Erratum 1 — §A3.6's keyframe must not animate opacity (defect D-51)

**What §A3.6 specifies:**

```css
@keyframes xp-surface { from { opacity: 0; transform: translateY(12px); } }
```

**What ships:**

```css
@keyframes xp-surface { from { transform: translateY(12px); } }
```

**Why the spec is wrong here.** A scroll-scrubbed animation has no transient
frames. Progress is bound to scroll position, so **every point in the range is a
resting state** — an intermediate alpha is not something the reader passes
through, it is where the text sits for as long as they leave the scroll there.
Text at reduced alpha composites toward the background and loses contrast.

Recomputed from `tokens.css` against `--bg #0d0d0c`, AA small text 4.5:1 — the
alpha at which each participating token first meets AA:

| Token | Element | Full-alpha ratio | Meets AA at |
|---|---|---|---|
| `--dim` | `.mono-meta` | 5.78:1 | **alpha ≥ 0.854** |
| `--accent` | `.numeral-sm` | 10.40:1 | alpha ≥ 0.618 |
| `--body` | `.receipt` | 12.11:1 | alpha ≥ 0.568 |
| `--ink` | `.display-xs` | 17.07:1 | alpha ≥ 0.478 |

`--dim` breaks first, having the least headroom at full strength. That is
exactly what the C-06 gate caught before the deploy: axe reported `[serious]
color-contrast` on `article:nth-child(3)` — the one row part-way through its
`entry 10% → 55%` range, hence at a fractional alpha. Rows sitting at alpha 0
were skipped by axe as not visible; the partially faded one was evaluated, and
failed.

**Why the fade was removed rather than floored.** Flooring the from-opacity at a
safe value means starting at alpha 0.854 — a 15% change over the whole range,
which is a fade nobody can perceive. The opacity channel is not worth its cost
at any value that is safe, so it is removed rather than reduced to a decorative
number. `translateY(12px)` carries the reveal on its own. `.receipt-rule` keeps
`scaleX` because a rule carries no text and therefore no contrast obligation.

**Consequence for the ledger:** A3.6's declared properties narrow from
`transform, opacity` to `transform`. Recorded rather than silently adjusted.

**Range-tuning would not have been a remedy.** Narrowing `animation-range` only
changes *which* scroll positions produce a sub-AA alpha, never *whether* one
exists. See the standing rule in `docs/decisions/STEP-08-P4.1-SCRUBBED-STATES.md`.

---

# v1.2 amendment: A3.7, the architecture diagrams (P5.4, 2026-08-27)

**Question it answers (C-12):** WHAT JUST HAPPENED. The entry's own pipeline assembles in reading order as the figure arrives, so the reader sees the flow rather than a finished picture.

**Scope:** `/projects/` only; one inline SVG per live entry (`templates/diagrams/`, generated by `tools/gen_diagrams.py` from each README).

**Mechanism:** `diagram.js` arms only a figure entirely below the viewport, then posts it once on intersection (timed, not scrubbed: D-51). Region labels, then each node followed by the edges that reach it. Nodes: `opacity 0 to 1`, `translateY(8px) to 0`. Edges: straight `<line>`s, `transform: scale(0) to 1` about their start point (`transform-box: fill-box`), which is how a line "draws" without leaving C-15's transform/opacity rule.

**Duration / easing:** `--motion-draw: 260ms`, `--ease-vt`; stagger `--motion-draw-step: 45ms` per item, capped at the fortieth. A 33-item drawing completes in about 1.7 s; every individual transition is 260 ms.

**Reduced motion (C-10, the single lever):** both tokens zeroed in the tokens.css block, and `.diagram.post-pending > *` neutralised there; `diagram.js` also declines to arm. **No JS:** nothing is ever hidden. **Above the fold / LCP / CLS:** untouched by construction; a diagram on screen at first paint is never armed.

**Zoom:** not motion. Instant width change inside the figure's own scrollable frame (A3.3 family).

**The guarantee that matters most to the owner:** transform and opacity cannot move a label relative to its box, so the drawing that animates is pixel-identical to the drawing at rest, and the generator refuses any drawing in which text overlaps (`REASON=DIAGRAM_OVERLAP`).

