# Interaction QA matrix

**The frozen project rule (handoff §6):** *no animation or overlay may block or overlap any interactive element in any state.*

That rule exists because the committed design was rebuilt after an earlier version's evidence layer covered the links column. This matrix is how the rule stops being a sentence and becomes something checkable, component by component, state by state.

**Scope:** every component the site ships, in every state it can be in.

## Evidence legend — what each mark actually means

The distinction matters more than the marks. A structural proof and a human looking at the thing are different kinds of evidence, and collapsing them would make this document flattering rather than useful.

| Mark | Means |
|---|---|
| **`C`** | **Verified structurally in code** — the property is asserted by a gate, a test, or a quoted rule. Proves the property exists; does **not** prove it feels right. |
| **`O`** | **Observed by the director** on the live site, with the date. The only evidence that the thing actually behaves. |
| **`—`** | Not applicable in this state (e.g. hover on a touch device). |
| **`?`** | **Not yet verified by either route.** Named, not hidden. |

I have no browser in this environment. **Every `O` in this table is the director's observation, never mine.** Nothing here is marked verified because I expected it to work.

## The overlay question, answered once

The site ships exactly one overlay: **A3.1**, the Home evidence layer. Everything else that changes on interaction changes colour or background in place, with no element stacked over another.

A3.1 satisfies the frozen rule by two independent properties, either of which alone would be sufficient:

1. **Bounded** — `left: calc(120px + var(--gap-grid))`, `right: calc(220px + var(--gap-grid))`. Derived from the grid tokens, so the bounds cannot drift away from the columns they clear. The layer ends before the links column begins.
2. **Inert** — `pointer-events: none`. Even if the bounds were wrong, the layer could not intercept a click.

Asserted by `test_evidence_layer_never_covers_the_links_column`. Observed clickable with the layer open by the director, 2026-08-06.

## Matrix

| # | Component | Rest | Hover | Focus-visible | Active | Keyboard-only | Reduced motion | Touch (no hover) |
|---|---|---|---|---|---|---|---|---|
| 1 | Nav link | `C` | `C O` instant colour swap, no transition | `C O` accent outline | `C` | `C O` reachable, logical order | `C` unaffected — no motion | `C` tap target ≥ label box |
| 2 | Nav current indicator | `C` accent + underline + ✓ | `—` non-interactive | `—` not focusable, deliberately | `—` | `C` skipped, no dead stop | `C` | `C` |
| 3 | Skip link | `C` off-screen | `—` | `C O` first tab stop, becomes visible | `C` | `C O` jumps to `#main` | `C` | `—` |
| 4 | **Home ledger row + A3.1 layer** | `C` layer `opacity: 0` | `C O` reveals, 200ms opacity only | `C O` reveals on `focusin` | `C` | `C O` tab into row reveals same evidence | `C O` reveals **instantly**, 0ms, still reachable | `C` layer hidden < 900px; all metrics inline |
| 5 | **Ledger links (REPO / CONTAINER / AS OF)** | `C` | `C O` colour swap | `C O` outline | `C` | `C O` **clickable with the layer open** | `C O` | `C` |
| 6 | Truth-strip clock | `C` no-JS shows `SNAPSHOT <stamp>` | `—` | `—` | `—` | `—` | `C` text tick is not motion | `C` |
| 7 | Projects slider (A3.2) | `C` scroll-snap, native scrollbar | `—` | `C` container focusable, it *is* a scroll region | `C` | `C O` arrow keys scroll | `C` native scroll unaffected | `C O` swipe, snap holds |
| 8 | Project card links | `C` | `C O` | `C O` | `C` | `C O` | `C` | `C` |
| 9 | Experience PDF button | `C` 1px accent border | `C O` inverts to solid accent | `C O` | `C` | `C O` | `C` no transition | `C` |
| 10 | **Receipts row (A3.4)** | `C` | `C` tint + body→bright, instant | `C` `:focus-within`, identical treatment | `—` | **`?`** see limit 1 | `C` instant, nothing to disable | `C` no hover, rest state only |
| 11 | Certification specimen tile | `C` dashed, labelled `VERIFIABLE` | `—` non-interactive | `—` | `—` | `C` no dead stop | `C` | `C` |
| 12 | Audit table rows | `C` | `—` | `—` | `—` | `C` | `C` | `C` restacks < 900px |
| 13 | Footer links | `C` | `C O` | `C O` | `C` | `C O` | `C` | `C` |

## Honest limits of this matrix

1. **Row 10, keyboard-only, is `?` and stays `?` until the data changes.** A3.4's focus half is `:focus-within`, and **no receipts row currently contains a focusable element** — so there is nothing to focus, and the focus state cannot fire on today's content. It is not broken; it is inert, by the ruling that chose it over `tabindex` (dead tab stops cost more against C-07/C-08 than they gain). Declared on /audit as A3.4's stated limit. The cell becomes verifiable the day a receipts row gains a link.

2. **Every `C` proves a property, not an experience.** `C` on "instant colour swap" means the CSS declares no transition. Whether a user perceives it as instant is `O`, and only `O`.

3. **Touch column is largely `C`.** The director's 375px pass (P3.2 close, DevTools plus a physical phone, all five pages) covers layout and overflow. Per-component touch *interaction* on a physical device is verified for the slider only.

4. **`active` states are structural throughout.** No component defines a distinct `:active` treatment; the column records that absence deliberately, rather than leaving it blank as though never considered.

## Where the observations came from

- **2026-08-06, P3.2 close** — 375px by eye in DevTools and on a physical phone, all five pages: no horizontal scrollbar, no side-to-side pan, full scroll depth.
- **2026-08-06, P3.3 review stop** — Home: evidence reveal instant and smooth; **links column clickable with the layer open**; keyboard tab pass clean with no dead stops; under emulated `prefers-reduced-motion` the reveal still functions with zero transition.
- **2026-08-06, link-by-link review** — every evidence link opened by hand. Produced defect report D-30, which measurement did not reproduce; the anchor stands as shipped.
