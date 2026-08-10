# Standing rule — every point in a scrubbed animation's range is a resting state

**Adopted:** 2026-08-10, owner ruling during P4.1 (STEP-08), on the evidence of
defect D-51.
**Scope:** every scroll-driven or otherwise scrubbed animation this site ships,
now and later. Not phase-limited.

## The rule

> A scrubbed animation has no transient frames. Its progress is bound to the
> reader's scroll position, so **every point in its range is a resting state**,
> and every one of them must satisfy **all static conditions** — contrast,
> interaction QA, focus visibility, hit targets, all of it.
>
> **Range-tuning is not a remedy.**

## Why this is not obvious, and why it cost a defect to learn

A timed animation is passed *through*. If a frame at 40% opacity exists for
80 ms on its way to 100%, no reader is sitting in it, and judging that frame
against a static contrast threshold would be a category error.

A scrubbed animation inverts that. Nothing advances it but the reader, and the
reader stops wherever they stop. A row at 40% opacity is not a frame in transit
— it is the state of the page for as long as that scroll position is held,
which may be a second or an hour. It is a rendering of the site, and it has to
be as correct as any other rendering.

D-51 is what that looks like when missed: A3.6 was specified with
`from { opacity: 0 }`, and the row part-way through its range rendered its
`--dim` metadata at a fractional alpha that composites to **below AA**. Not for
an instant — for as long as the reader left it there.

## Why range-tuning cannot fix it

The tempting response is to narrow `animation-range` so the faded portion falls
somewhere less exposed. That changes **which** scroll positions produce a
failing state; it never changes **whether one exists**. The bad state is still
reachable, still resting, and still a rendering of the page. A remedy that
relocates a defect is not a remedy.

The honest fixes are to remove the offending channel, or to bound it so that
**every** value in the range passes — chosen by calculation and shown, never by
eye. D-51 took the first: `--dim` only clears AA at alpha ≥ 0.854, so a safe
fade would have been a 15% change nobody can see. A channel that must be
imperceptible to be correct is not worth having.

## What this rule binds

1. **Any property that affects contrast** — `opacity`, `color`, `filter`,
   `background-color`, `mix-blend-mode` — may be scrubbed on a text-bearing
   element only if the condition holds across the **whole** range, proven by
   calculation.
2. **Any property that affects interaction** — `transform` that moves a control,
   `pointer-events`, anything changing hit geometry — must keep every
   interactive element reachable and non-overlapping at every point in the
   range (handoff §6, `INTERACTION-QA.md`).
3. **Geometry** stays CLS-safe throughout, not merely at the endpoints.

`transform: translateY` and `scaleX` on non-text elements are unaffected: they
move things without altering contrast, which is why A3.6's reveal survives as
translate-only and `.receipt-rule` keeps its `scaleX`.

## How it is enforced

**Structurally, at build time, as of 2026-08-10.** The control was proposed at
the P4.1 review stop rather than silently added, and approved as designed.

`tools/check_animations.py` → `check_scrubbed_contrast()`, reason code
`SCRUBBED_CONTRAST_RISK`. For every entry whose `duration_type` is `scrubbed`,
it refuses a contrast-affecting property — `opacity`, `color`, `filter`,
`background-color`, `background`, `mix-blend-mode` — inside any keyframe that
entry declares.

**It is deliberately blunt, and the bluntness is the honesty.** CSS alone cannot
tell which tokens a selector's subtree actually renders, so a checker that tried
to compute the composited ratio would be guessing with more decimal places.
Refusing what cannot be verified beats pretending to compute it.

**The escape, and its price.** An entry may declare `contrast_proof` naming the
computed floor at which every participating token still meets AA. That keeps
this from being a rule obeyable only by never fading anything — but it costs a
stated calculation, shown in the commit, which is the point.

Controls run in both directions on every build:

| Control | Must |
|---|---|
| `xp-surface` **with** `opacity` — D-51 itself | **refuse** |
| the shipped transform-only `xp-surface` | pass |
| an entry declaring `contrast_proof` | pass |
| a **timed** entry fading text (A3.5) | pass — a timed frame is passed through, not rested in |

The last row is the distinction the whole rule turns on, so it is asserted
rather than assumed: A3.5 animates opacity at 250 ms and is correct to. C-06's
axe gate still runs as the backstop that originally caught D-51.

## Related record

- Defect **D-51** — the failure that produced this rule.
- **Erratum 1** against `MOTION_SPEC_v1_1.md` — the spec change it forced.
- **C-09** (contrast), **C-06** (axe), **C-15** (motion properties),
  handoff §6 (interaction QA).
