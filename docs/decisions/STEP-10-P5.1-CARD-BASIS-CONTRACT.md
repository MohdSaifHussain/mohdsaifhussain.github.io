# STEP-10: P5.1 — The card's basis sentence tells the truth per entry

**Project:** mohdsaifhussain.github.io | **Phase:** P5.1 | **Date:** 2026-08-22
**Status:** Built 2026-08-22; review stop passed on the owner's ruling; awaiting the owner's phase-close read and push go. Outcome below.
**Tier:** STANDARD — a public template change that ends in a deploy, on the same CI path two content pushes used today. Re-asked at kickoff; FULL's rehearsal adds nothing a local build and the owner's eye do not already give here.
**Depends on:** content updates CU-1..CU-4 (four bases defined; OWNER-MEASURED retired).

**Authority:** C-34 forbids template edits for content changes. This is not a content change: the sentence is site chrome that was true for every card on 2026-08-06 and is true for one card of six on 2026-08-22. Defect D-60.

## 1. Objective

Every project card states how its figures were obtained, per its own declared `metrics_basis`, and the build refuses to render a basis the record has not defined or has retired.

**Exit criterion:** the owner opens /projects locally and reads six cards; each basis sentence matches the basis the data file declares for that entry, and the build refuses a deliberately wrong basis with a named reason.

## 2. Deliverables

| ID | Deliverable | Governing standard |
|---|---|---|
| D1 | `build.py`: `BASIS_SENTENCES`, one per basis in use; `_basis_sentence` attached per entry; `BASIS_UNKNOWN` and `BASIS_RETIRED` refusals | C-34 (StrictUndefined spirit: a missing meaning fails the build), doctrine rule 5 |
| D2 | `templates/projects.html.j2`: the card prints `p._basis_sentence` | C-34, by this contract |
| D3 | Tests: every rendered card's sentence matches its entry's basis (positive, all three bases in use); unknown basis refused `BASIS_UNKNOWN`; `owner-measured` refused `BASIS_RETIRED` (negative) | doctrine rules 5 and 14 |
| D4 | `/audit` A4.6 reason text and `tools/fetch_stats.py` docstring no longer say figures remain baselines or that TS-Sentry is owner-measured | D-37 (no published statement outlives its truth) |
| D5 | D-60 in DEFECTS, decision 5.1.1 in DECISIONS, this contract's outcome | C-31 |

## 3. Requirements

- The four wordings are the owner's ruling of 2026-08-22, verbatim (section 2 of the session record; restated in `build.py`).
- `owner-measured` stays in the allowed set of `test_metrics_basis_agrees_with_entries` (it is a defined basis) but has no sentence: declaring it refuses the build, because clause (2) of `_metrics_basis` says nobody uses it.
- No em-dash in any new rendered text (C-27 scope, CU-2).
- Nothing in `data/projects.json` changes.

## 4. Out of scope

The visit counter (A4.4, D-03) — a separate ruling. Any change to how figures are measured. The home page, which prints no basis sentence.

## 4a. Review stop

After D1-D3 are green: the builder shows the diff and the three refusal outputs verbatim; the owner rules before D4-D5 and before any push.

## 5. Exit checklist

- [ ] Six gates exit 0, `--verify-links` exit 0
- [ ] Negative controls shown refusing with distinct reason codes
- [ ] Owner reads six cards locally: sentence matches basis on each
- [ ] D-60, 5.1.1, outcome written; pushed on the owner's go; CI green; live page re-read

## 6. Outcome

### Exit checklist, evidenced

- Six gates exit 0 (build, pytest 71 passed / 1 skipped D-32, c33, content, animations, contrast); `--verify-links` exit 0. Run by the builder 2026-08-22 after D5.
- Negative controls through the real `build.py`: `REASON=BASIS_UNKNOWN opskit: 'vibes' has no basis sentence...` exit 1; `REASON=BASIS_RETIRED opskit: 'owner-measured' is retired...` exit 1. Positive control: real data, exit 0. `projects.json` byte-identical after.
- Owner's read of six cards: **pending the phase-close ritual**.
- D-60, 5.1.1, this outcome: written. Push: pending the owner's go.

### Deviations

- D4 (A4.6 text, fetch_stats docstring) was built before the §4a review stop rather than after it; shown at the stop, accepted by the owner's ruling. Recorded, not absorbed.

### Carried

- Nothing deferred. The visit counter (A4.4) was out of scope and remains a separate ruling.
