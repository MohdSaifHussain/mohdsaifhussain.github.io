# M-3 — Cursor / click state: STRUCK

**Filed:** 2026-08-10, P4.1 (STEP-08) · **Ruled by:** the owner, at the design
session close recorded in `MOTION_SPEC_v1_1.md`
**Status:** STRUCK before design. Nothing in this build implements it.

## What M-3 was

A scoped interaction mark — a brief ledger-tick or ink-dot confirmation at the
click point on interactive elements, `pointer-events: none`, opacity and
transform only, ≤ 250 ms. Explicitly **not** a site-wide custom cursor, which
was rejected earlier for usability and disorientation risk.

It originated as the owner's own parked request from P3.2, deferred at the time
"for discussion after P3.3 motion lands." Motion landed, so it came back for a
ruling.

Its proposed C-12 answer was WHAT JUST HAPPENED.

## The ruling

Quoted from the design authority, `MOTION_SPEC_v1_1.md`, ruling line:

> M-3 STRUCK as pre-registered — no interactive surface is non-redundant (nav
> has M-1; links have A3.3 plus the navigation itself) and every other surface
> would be a false affordance. Selection rule satisfied: 2 of 3. A3 ledger grows
> 4 → 6 entries.

## Why this is the right outcome, stated in full

The verdict was **pre-registered**: the reviewer recorded STRIKE BEFORE DESIGN
as the recommended outcome *before* the design session ran, so the session could
not rationalise its way into shipping it. The owner confirmed the strike at the
ruling.

The reasoning has two halves, and both have to hold:

1. **On interactive surfaces it is redundant.** Registration feedback already
   exists everywhere a click can land. A3.3 is the instant colour swap on links
   and nav. A3.4 is the Experience row reading state. And A3.5, ruled in by this
   same amendment, *is* click feedback on the nav — the ledger-turn is the
   response to the click. A mark added on top would be a second answer to a
   question already answered.

2. **On non-interactive surfaces it is dishonest.** A click mark on a surface
   that does nothing advertises an affordance that does not exist. That is the
   same C-12 failure caught in P3.3, where A3.4 was declared WHERE AM I rather
   than WHAT CAN I DO precisely because the receipts rows carry no control.

There is no surface where M-3 is both non-redundant and honest. The brief's own
rule decides it: **redundant motion is rejected motion, including motion the
owner asked for.**

## Honest limit of this record

The design authority's closing line refers the reasoning to "the design
session's 1f verdict card." **That verdict card is not in this repository.** The
reasoning recorded above is quoted from the spec's own ruling line and expanded
against conditions and prior decisions that *are* in the repository (C-12, A3.3,
A3.4, A3.5, the P3.3 Q1 ruling). Nothing here is reconstructed from a document
that cannot be read — where the card would have added detail, this file is
simply shorter rather than inventing it.

## Consequences

- The A3 declared ledger grows **4 → 6**, not 4 → 7. The selection rule "ship at
  most 2 of the 3" is satisfied by A3.5 (M-1) and A3.6 (M-2).
- No CSS, no marker comment, and no `audit-spec.json` entry exists for M-3. The
  animation gate's `UNSHIPPED_ANIMATION` direction would refuse a declaration
  without an implementation, so a struck move cannot be half-recorded.
- The owner's original P3.2 request is now **discharged by ruling**, not still
  parked. It does not carry forward as an open obligation.

---

# Erratum against a closed phase's record — R-05's role count

Found 2026-08-10 while grounding `MOTION_SPEC_v1_1.md` against the artifacts it
describes. Filed here because it was found in this phase; it is **an erratum
against STEP-04's record, not a defect against STEP-04**, which met its exit
criterion. Per Template 7's supersession convention the original text stays and
the correction sits beneath it, in `STEP-04-P3.2-CONTRACT.md`.

**What it says:** reading R-05 states that the Experience page "derives all five
roles uncurated from `experience.json`."

**What is true:** `experience.json` contains **six** roles, and has contained six
for its entire history — it has a single commit, `4e8a169`, and the file already
held six at `8d2f9e0`, the P3.2 close. The live page renders `06 ROLES,
RECEIPTED`. The count was never five.

**What is unaffected:** R-05's substance. The reading is about *curation* — that
the identity strip renders the owner-authored `headline_employers` (four
employers) while Experience derives every role uncurated. That distinction holds
exactly as recorded; only the number attached to it is wrong.

**How it was found, and why that matters:** by re-deriving the count from
`experience.json` rather than quoting the sentence — doctrine rule 13. It
survived the P3.5 release and the post-release deviation audit of 2026-08-09,
because that audit checked *displayed values against data* and did not check
*documentation prose against data*. That is a real gap in the audit's coverage
and has been recorded as such in the audit command's item 9, which now says to
grep the data files and not only the docs.
