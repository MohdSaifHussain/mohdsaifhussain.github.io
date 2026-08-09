# STEP-08: P4.1 — Signature Motion (v1.1)

**Project:** mohdsaifhussain.github.io | **Phase:** P4.1 | **Date:** 2026-08-10
**Status:** Specified, not started
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

- [ ] `check_animations.py` reports six declared, six shipped, both directions
- [ ] Its selftest passes, including a NEW control in each direction for the
      keyframes sweep: an undeclared `@keyframes` must refuse, a declared one
      must be accepted
- [ ] `SCROLL_NOT_NATIVE` and `MOTION_NOT_REDUCED` pass over the new CSS
- [ ] Exactly one `prefers-reduced-motion` block in the shipped CSS, asserted
- [ ] `audit-spec.json` declares six entries; A3.6's duration is `scrubbed`,
      and no millisecond value appears for it anywhere
- [ ] D5's above-fold check runs in a real browser and **refuses** when fed an
      element that starts hidden above the fold (negative control), and accepts
      the real page (positive control)
- [ ] Six SOP gates exit 0; full suite green
- [ ] `/audit` shows `06 ANIMATIONS SHIP`, derived, no typed count
- [ ] Measured under protocol: LCP and CLS published as measured
- [ ] Owner's eye check on the live site: ledger-turn across all five pages,
      the Experience reveal scrubbing on scroll-up, and the reduced-motion
      toggle collapsing everything
