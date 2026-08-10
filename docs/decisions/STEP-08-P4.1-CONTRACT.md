# STEP-08: P4.1 — Signature Motion (v1.1)

**Project:** mohdsaifhussain.github.io | **Phase:** P4.1 | **Date:** 2026-08-10
**Status:** **Closed 2026-08-10.** D1-D8 shipped; the A3 ledger grows 4 -> 6
by recorded ruling. Five defects found, four of them by machinery refusing
rather than by inspection. Eye check performed personally by the director on
the live site: all four scenarios as expected, finding 5 clean.
**Tier:** FULL — the artifact is a public site, the act is a deploy, and the
motion is the first thing a visitor sees.
**Depends on:** STEP-07 (P3.5) closed — v1.0.0 released, `d0a8439`, and the
post-release deviation audit closed D-46, D-47, D-48. Specifically depends on
D-48's machinery: `tools/gate_status.py`, the six-gate A2 ledger, and the two
gates `SCROLL_NOT_NATIVE` / `MOTION_NOT_REDUCED` added to
`tools/check_animations.py`, which were built to police exactly this work.

**Design authority:** `MOTION_SPEC_v1_1.md` (FINAL, design session closed by
owner ruling 2026-08-10), committed with this phase on the precedent of
`STEP-02-HANDOFF.md` — a design authority that is not in the repository cannot
be cited by a reviewer who has only the repository.

The spec was produced under a prior document, `MOTION_BRIEF_v1_1_REVIEWED.md`,
which governed the design session and carried the adversarial review. **The owner
has deliberately excluded that brief from the repository** (instruction,
2026-08-10). So no requirement here cites it: the constraints it contributed —
the degrade-to-visible rule, the canonical C-12 question set, and M-2's
one-sentence orientation test — are restated inline below as requirements 3.7,
3.9 and in D1, and are checkable from this repository alone. Its one binding
sequencing rule, that the gate updates land in the same commit as the first new
animation, is carried as the D2/D3 commit rule.

This is a deliberate deviation from doctrine rule 3's "cite the source": the
source is unavailable by the owner's choice, so the requirement is carried
rather than cited. Recorded here rather than left implicit.

**Standing rule:** every implementation follows the top applicable standard.
Each requirement below names its governing standard.

## 1. Objective

Ship the two signature motion moves ruled in by the owner — A3.5 (cross-document
view transition, vertical ledger-turn) and A3.6 (scroll-driven reveal on the
Experience register) — growing the declared A3 ledger from four entries to six,
under the existing gates and with the single C-10 reduced-motion lever intact.

**Exit criterion:** the owner navigates the live site between all five pages and
sees the ledger-turn; scrolls `/experience/` down and back up and sees the
register scrub; toggles reduced motion and sees every one of the six declared
animations collapse — with `/audit` publishing all six entries and the measured
numbers republished under the standing protocol.

## 2. Deliverables

| ID | Deliverable | Governing standard(s) |
|---|---|---|
| D1 | M-3 recorded STRUCK in `docs/decisions/`, with the reasoning quoted from the spec's own ruling line. Includes the R-05 role-count correction found while grounding the spec | MOTION_SPEC ruling; Template 7 supersession |
| D2 | A3 declaration schema gains `duration_type: ms \| scrubbed`; `audit-spec.json` declares A3.5 and A3.6; `check_animations.py` goes two-directional over six entries and its keyframes sweep learns declared-vs-undeclared, with controls both directions | ruling condition (1); C-12 |
| D3 | A3.5 shipped: `@view-transition`, the three `view-transition-name` groups, `--motion-vt` token, and the lever reaching it inside the ONE existing reduced-motion block | MOTION_SPEC §A3.5; C-15, C-10, C-19 |
| **—** | **REVIEW STOP** — after D2+D3, before D4 | ruling: "one review stop" |
| D4 | A3.6 shipped: `animation-timeline: view()` on `.xp-row` and `.receipt-rule`, `@supports`-wrapped, `animation: none` in the same reduced-motion block | MOTION_SPEC §A3.6; C-10, C-15, C-19 |
| D5 | Above-fold protection proven by execution: no element inside the first-paint viewport of `/experience/` carries a hidden from-state | ruling condition (4); C-02 |
| D6 | `/audit` renders the six-entry ledger with the scrubbed duration shown honestly | ruling condition (6); C-30, C-35 |
| D7 | Design note recording the C-10 lever widening from one variable to one mechanism | ruling condition (2); MOTION_SPEC §A3.5; C-10 |
| D8 | Measured under the standing protocol and published as measured | ruling condition (5); C-01, C-02 |

**D2 and D3 land in ONE commit.** Ruling condition (1): `check_animations.py`
is updated two-directionally to the new declared list *in the same commit* as
the first new animation. A gate that lags its list is D-24's lesson repeated.

## 3. Requirements

- **3.1** The A3 declared list grows 4 → 6 and no further. Both directions stay
  enforced: motion shipping undeclared refuses (`UNDECLARED_ANIMATION`), motion
  declared but not shipped refuses (`UNSHIPPED_ANIMATION`). *Standard: C-12.*
- **3.2** The keyframes sweep stops refusing unconditionally. Every shipped
  `@keyframes` must be claimed by a declared A3 entry; every keyframe name a
  declared entry claims must exist in the CSS. Both directions get a control.
  *Standard: C-12; ruling condition (1).*
- **3.3** No invented millisecond value anywhere. A3.6's duration is the enum
  value `scrubbed`, never a number. *Standard: ruling condition (1); C-27 —
  a fabricated figure is the defect this site exists to demonstrate against.*
- **3.4** A3.5's duration is driven by `--motion-vt`, not a literal, so the C-10
  lever reaches it. *Standard: MOTION_SPEC §A3.5 prose; C-10.*
- **3.5** Exactly ONE `@media (prefers-reduced-motion: reduce)` block exists in
  the shipped CSS, and both new behaviours live inside it. *Standard: ruling
  condition (2); C-10. Also structural: `reduced_motion_body()` reads the first
  match only, so a second block would be invisible to the gate.*
- **3.6** `SCROLL_NOT_NATIVE` and `MOTION_NOT_REDUCED` must pass over the new
  CSS. **If either fires on the spec as written, stop and report — do not adjust
  the gate.** *Standard: ruling condition (3).*
- **3.7** A3.6 is wrapped in `@supports (animation-timeline: view())`. Content is
  never hidden behind an API the browser lacks; degrade to visible, never to
  hidden. *Standard: C-10 applied to feature detection — motion-off includes
  API-absent. Carried from the design brief's degrade rule, restated here
  because that brief is not in the repository.*
- **3.8** Zero third-party resources. No library, no JS scroll listeners.
  *Standard: C-19.*
- **3.9** Every declared answer is one of the three canonical C-12 questions.
  Both new entries answer WHERE AM I. *Standard: C-12.*
- **3.10** Official sources fetched before implementing the two CSS APIs, cited
  by URL in the commit. No working from memory on API shape or support.
  *Standard: doctrine rule 3.*
- **3.11** LCP must not regress past 1.65 s; CLS stays 0.000. If either
  regresses, the responsible move is reverted. Numbers publish as measured
  either way. *Standard: ruling condition (5); C-02.*

## 4. Out of scope

- Light mode, the owner SOP walkthrough, the NVDA remaining-pages pass, and
  CI-published stats. All remain queued v1.1 items under separate rulings.
- M-3 in any form. Struck by ruling; D1 records it, nothing implements it.
- Any change to `SCROLL_NOT_NATIVE` or `MOTION_NOT_REDUCED` that would make a
  failing spec pass. Fenced by 3.6.
- Reopening P3.5 or earlier. The R-05 correction in D1 is an erratum against a
  closed phase's *record*, explicitly not a defect against the phase, which met
  its exit criterion.

## 4a. Review stop

Halt after **D3**, before **D4**.

The split falls there because D2 *relaxes a refusal*: the keyframes sweep stops
refusing every `@keyframes` unconditionally. That is the single riskiest edit in
this phase — every other change adds motion under a gate, this one widens what a
gate permits. D4 is the deliverable that most depends on the relaxation, so the
relaxation gets reviewed after it exists and before the thing it permits is
built. Stop before the thing sets, not after.

**Carried to the stop for the director's ruling — question Q3, raised at plan
time and deliberately not decided by the builder:**

`check_reduced_motion()` inspects `transition:` declarations only. Both new
animations are `animation:` declarations, and `--motion-vt` is consumed inside
an `animation` shorthand. So `MOTION_NOT_REDUCED` will **pass over the new
motion without inspecting it** — a vacuous pass, D-32/D-44's exact shape.
Separately, the `ANIMATION` regex at `check_animations.py:66` is defined and
never called, so C-15's transform/opacity restriction and 400 ms ceiling apply
to nothing that ships as a keyframe animation.

Requirement 3.6 forbids adjusting those gates so the spec passes. Extending them
to *cover* keyframes is the opposite — strengthening — but it is still a change
to a fenced gate, so the director rules, not the builder.

## 5. Exit checklist

- [x] `check_animations.py` reports six declared, six shipped, both directions
      - *`declared animations (6): A3.1 … A3.6`; `implemented in CSS` the same,
        each marked `@ships A3.N`. Keyframes both ways: 4 declared, 4 shipped.*
- [x] Its selftest passes, including a NEW control in each direction for the
      keyframes sweep: an undeclared `@keyframes` must refuse, a declared one
      must be accepted
      - *36 controls pass. Both keyframe directions, both D-49 marker
        directions, both C-10 animation directions, and four
        `SCRUBBED_CONTRAST_RISK` controls.*
- [x] `SCROLL_NOT_NATIVE` and `MOTION_NOT_REDUCED` pass over the new CSS
      - *Both PASS. Neither weakened; `MOTION_NOT_REDUCED` was DEEPENED under
        ruling after being proved blind (D-50).*
- [x] Exactly one `prefers-reduced-motion` block in the shipped CSS, asserted
      - *`test_exactly_one_reduced_motion_block_ships`, counted in `_site`.*
- [x] `audit-spec.json` declares six entries; A3.6's duration is `scrubbed`,
      and no millisecond value appears for it anywhere
      - *`duration_type: scrubbed`, rendered `scroll-scrubbed`; asserted by
        `test_scrubbed_animation_never_publishes_a_millisecond_value`.*
- [x] D5's above-fold check runs in a real browser and **refuses** when fed an
      element that starts hidden above the fold (negative control), and accepts
      the real page (positive control)
      - *CI run `31343145429`: `[PASS] poisoned page refused (exit 1)`;
        `[PASS] real page accepted (exit 0)`; mobile 375x667 and desktop
        1280x800.*
- [x] Six SOP gates exit 0; full suite green
      - *All six `exit=0`. 62 tests: 61 passed, 1 skipped loudly with its reason
        (D-32's guard). Four tool selftests green.*
- [x] `/audit` shows `06 ANIMATIONS SHIP`, derived, no typed count
      - *Rendered from `a3_animations | length`; `COUNT_LITERAL` clean.*
- [x] Measured under protocol: LCP and CLS published as measured
      - *LCP 1.55 s (worst median), CLS 0.000 (worst median), 30 runs, published
        origin. Published exactly as measured; nothing re-run for a better
        number.*
- [x] Owner's eye check on the live site: ledger-turn across all five pages,
      the Experience reveal scrubbing on scroll-up, and the reduced-motion
      toggle collapsing everything
      - *Performed personally by the director on the live site, 2026-08-10. All
        four scenarios as expected; finding 5 clean. Table in the Outcome.*

---

## 6. Outcome

**Shipped:** D1-D8, live at `e834294`. The A3 declared ledger grows 4 -> 6 by
recorded ruling. 62 tests green with one deliberate loud skip; six SOP gates and
four tool selftests at exit 0; served bytes byte-identical to the built tree on
all five pages.

### Measured, under the standing protocol

Median of 3 runs per page per profile, both profiles, against the published
origin. 30 reports. Corrected implementation (D-52).

| Metric | Measured | Condition |
|---|---|---|
| Lighthouse, worst median | 100 / 100 / 96 / 92 | C-01 UNMET, declared |
| **LCP, worst median** | **1.55 s** | **C-02 UNMET, declared** — the 1.65 s ceiling was not breached |
| CLS, worst median | **0.000** | C-02 CLS MET |
| axe | 0 violations | C-06 MET |
| W3C validator | 0 errors | C-23 MET |
| Home first-view transfer | 143,396 B | C-03 MET |

The motion cost **0.01 s of LCP** — 1.54 s before it, 1.55 s after, both under
the corrected implementation. The spec's revert rule was not triggered.

### Phase close, verified

Performed personally by the director on the live site, 2026-08-10.

| Scenario | Expected | Observed |
|---|---|---|
| Navigate between all five pages | header and footer hold still; `main` turns out and in | **As expected** — header and footer held still with the turn playing |
| Nav current-marker during a turn (finding 5) | changes as state, instantly, not as a crossfade | **Clean** — the marker snapped instantly, no ghosting |
| `/experience/`, scroll down then back up | rows and rules scrub forward and reverse | **As expected** — scrubbed in both directions |
| `prefers-reduced-motion: reduce`, repeat both | instant swap; register fully visible and static | **As expected** — everything instant and fully visible |

**The row worth keeping in view:** the reduced-motion row. It is the only one
that demonstrates a *limitation working* — the single C-10 lever collapsing six
declared animations at once, on the real site, observed rather than asserted.
It is also the row D-50 proved the machinery could not check on its own.

**Finding 5 is closed by observation.** It was raised at the review stop as a
risk that the `site-header` snapshot would crossfade a changing current-marker
and produce motion the ledger does not declare. It did not. No widening of
A3.5's declaration text and no separate `view-transition-name` were needed.

### Defects found by running it, not by inspection

Five. **Four were found by machinery refusing**, and none by reading code.

1. **D-49** — a declared animation could be marked shipped by *mentioning* its
   id. `shipped_ids()` matched any `A3.N` anywhere, including ordinary comment
   prose, and both stylesheets discuss entries by id constantly. Caught
   red-handed: a comment reading "A3.6 is scrubbed" made the gate report A3.6 as
   implemented while no A3.6 CSS existed. The `UNSHIPPED_ANIMATION` direction
   had been satisfiable by prose since P3.3.
2. **D-50** — `MOTION_NOT_REDUCED`, built in P3.5 to enforce C-10, scanned
   `transition:` declarations only and was therefore blind to both v1.1
   animations. Deleting `--motion-vt: 0ms` left A3.5 running its full 250 ms
   turn for a visitor who had requested reduced motion, and the checker printed
   *"motion is switchable off (C-10)"* and exited 0. Found by sabotage at the
   review stop; no amount of argument would have found it.
3. **D-51** — scrubbed opacity on text. A scrubbed animation has no transient
   frames, so an intermediate alpha is a *resting* state, and `--dim` drops
   below AA under alpha 0.854. Found by the C-06 axe gate refusing the deploy.
   Nothing reached the published site.
4. **D-52** — LCP, CLS and the transfer figure never followed the median-of-3
   protocol printed beside them on /audit. Found by refusing to act on a 2.32 s
   figure that would have triggered a revert of work whose true cost was 0.01 s.
5. **A control silently obsoleted by its own fix** — D-49's marker change broke
   the existing undeclared-animation control, which failed rather than passing
   quietly. Not logged as a defect: the control did exactly its job.

### Readings and deviations, recorded

- **R-13** — the spec's A3.5 code block shows a `250ms` literal while its prose
  requires `var(--motion-vt)`. Prose governs; the literal would put the duration
  permanently beyond the C-10 lever. DECISIONS 4.1.3.
- **R-14** — element selectors sit in `tokens.css`, inside the lever block. A
  layering exception, taken because a second block would be two levers and would
  be invisible to `reduced_motion_body()`. DECISIONS 4.1.2.
- **R-15** — `duration_type` is `ms | scrubbed | none`, a third value beyond the
  ruling's literal two. A3.2 is native scrolling with no duration at all; typing
  it `ms` would be the invented value the same ruling forbids. Confirmed by the
  director at the review stop. DECISIONS 4.1.4.
- **Deviation, D3/D4 sequencing.** Ruling condition (1) asked for the six-item
  list in the same commit as the first new animation. Declaring A3.6 before its
  CSS makes the gate red — correctly, that is the `UNSHIPPED_ANIMATION`
  direction working — and literal compliance would have merged D3 and D4 and
  deleted the review stop the same ruling ordered. The protected invariant, that
  the gate never lags its list at any commit, held at every commit. Confirmed by
  the director. DECISIONS 4.1.6.
- **Deviation, the design brief is not in the repository**, by the owner's
  instruction. No requirement cites it; the three constraints it contributed are
  restated inline as requirements 3.7 and 3.9 and in D1. A deviation from
  doctrine rule 3's "cite the source", recorded rather than left implicit.
- **Erratum 1 against `MOTION_SPEC_v1_1.md`** — §A3.6's opacity channel removed.
  Spec text left intact.
- **Erratum 2 against STEP-07 and the `v1.0.0` tag message** — the released
  1.65 s LCP was a worst single run; 1.53 s under its own protocol. Pessimistic
  in direction, non-conformant in method. Original text left intact.
- **Correction to R-05 in STEP-04** — "all five roles" was never true; the
  register has always held six. An erratum against a closed phase's *record*,
  explicitly not a defect against the phase, which met its exit criterion.

### Obligations

**Discharged:** the v1.1 motion amendment in full. M-3 struck by ruling and
filed, which also discharges the owner's parked P3.2 cursor request — it is no
longer an open item.

**New standing rule, not phase-limited:** every point in a scrubbed animation's
range is a resting state and must satisfy every static condition; range-tuning
is not a remedy. `STEP-08-P4.1-SCRUBBED-STATES.md`, enforced structurally by
`SCRUBBED_CONTRAST_RISK` with the `contrast_proof` escape.

**Carried, unchanged:** C-08's four screen-reader-unverified pages (A4.9);
C-36's owner SOP walkthrough; light mode (A4.8); CI-published stats. All were
explicitly out of scope and remain separate rulings.

### Honest limits

- **The eye check was performed in Chrome; the version was not recorded.** Both
  features are Limited availability / not Baseline, so the pass evidences
  Chrome and nothing else — no claim is made here about Firefox or Safari, and
  the version is unstated, so it cannot be tied to a specific engine release.
- **A3.5 and A3.6 are invisible on non-supporting browsers, by design.** Those
  visitors get plain navigation and a static register. That is the declared
  degrade, verified by construction — an ignored at-rule and an `@supports`
  wrapper — not by observation on such a browser.
- **The reduced-motion pass was emulated**, not taken from a system-level
  preference on a machine configured that way.
- **No screen-reader pass covers the new motion.** A3.5 and A3.6 are
  transform-only and announce nothing, but that is a reasonable expectation
  rather than an observation, and this site does not publish one as the other.
  It joins A4.9 rather than narrowing it.
- **`SCRUBBED_CONTRAST_RISK` is blunt by design.** It refuses the channel rather
  than computing composited contrast, because CSS alone cannot tell which tokens
  a selector's subtree renders. A future entry wanting a legitimate faded reveal
  must state a `contrast_proof`; the checker will not derive one.
