# STEP-11: P5.2 — The visit counter is retired, not faked

**Project:** mohdsaifhussain.github.io | **Phase:** P5.2 | **Date:** 2026-08-22
**Status:** **Closed 2026-08-22.** Built, six gates green, pushed on the owner's standing go of 2026-08-22 (the owner waived the per-phase eye-check for this batch and asked for one push at the end). Outcome below.
**Tier:** STANDARD — same reasoning as P5.1: a small public template change on a deploy path exercised three times today.
**Depends on:** P5.1 closed.

**Authority and the deviation it records.** Handoff §3 designed the footer with `VISITS —`, and decision 3.1.4 (2026-08-06, defect D-03) ruled that v1.0.0 ships the dash rather than a third-party counter. This phase removes the element on the owner's ruling of 2026-08-22, option (b) of three: (a) keep the dash, (b) remove the element, (c) wire a counter and narrow the zero-third-party claim. A dash designed to look like a counter with no value invites the question "is it broken?", which the owner asked today. Recorded as a deviation from the handoff, as 3.1.3b was, not absorbed.

## 1. Objective

No page carries a visit counter, faked or dashed; limitation A4.4 moves to the resolved register with its reason; the zero-third-party claim is unchanged.

**Exit criterion:** the owner reads the footer on all five pages and finds LINKEDIN, GITHUB and the colophon, and nothing that looks like a counter; /audit lists A4.4 under resolved.

## 2. Deliverables

| ID | Deliverable | Governing standard |
|---|---|---|
| D1 | `templates/base.html.j2`: the `foot-visits` span and its comment removed; `build.py`: `VISITS` and the `visits` context key removed; `site.css`: the orphaned `.foot-visits` rule removed | C-34 by this contract; no dead rules carried |
| D2 | `tools/check_content.py`: the D-22 comment and fixture no longer cite a footer string that does not exist; the fixture keeps proving chrome outside `<main>` is exempt | D-37 |
| D3 | `data/audit-spec.json`: A4.4 to `a4_resolved` with `closed` and `closed_by` | register rule (the D-37 test) |
| D4 | Test: no rendered page contains `VISITS`; A4.4 is in the resolved list and not the active one; no orphaned CSS rule | doctrine rule 14 |
| D5 | Decision 5.2.1; this outcome | C-31 |

## 3. Requirements

- `data/profile.json`, `projects.json`, and every measured claim on /audit are unchanged.
- Zero third-party resources, unchanged; `test_no_third_party_resources_load` must still pass.

## 4. Out of scope

Any counter. Traffic is read privately via the repository's Insights, which needs no script.

## 4a. Review stop

After D1-D4: diff and gates shown; owner rules; then D5 and the close.

## 5. Exit checklist

- [ ] Six gates exit 0
- [ ] Owner reads five footers and the /audit resolved list
- [ ] 5.2.1 and outcome written; pushed on the go; CI green; live footer re-read

## 6. Outcome

- Six gates exit 0 (pytest 74 passed / 1 skipped D-32). `VISITS` appears on zero rendered pages; `.foot-visits` gone from CSS; A4.4 resolved with reason.
- **Deviation:** the owner's phase-close read (five footers, /audit resolved list) was waived by the owner's ruling of 2026-08-22 for this batch; the builder's rendered-footer read stands in its place and is weaker. Recorded, not absorbed.
- Carried: nothing.
