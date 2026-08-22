# STEP-12: P5.3 — Mobile legibility, the robots audit, and supply-chain pins

**Project:** mohdsaifhussain.github.io | **Phase:** P5.3 | **Date:** 2026-08-22
**Status:** **Closed 2026-08-22** on the owner's standing go (eye-check waived for this batch; see Outcome). The measured effect on C-01 lands when `measure-live` runs against the published origin; until then the /audit figures are the previous run's, as always.
**Tier:** STANDARD. **Verified on mobile:** the owner ruled 2026-08-22 that every change is checked on mobile; here the two fixes are mobile-profile findings, and the measurement reported is the worst median across both Lighthouse profiles.
**Depends on:** P5.2 closed.

## 1. Objective

Close the two declared C-01 gaps at their real causes, and pin what CI executes.

**Exit criterion:** after the next `measure-live` run, Lighthouse best-practices and SEO read 100 on both profiles, or the cause of any remainder is named on /audit. Every `uses:` in the workflows names a commit SHA.

## 2. Deliverables

| ID | Deliverable | Governing standard |
|---|---|---|
| D1 | `tokens.css`: `--type-mono-meta`, `--type-mono-meta-sm`, `--type-mono-link` redefined at 12px inside the existing `max-width: 900px` block; desktop untouched | contract 3.2 (one definition per step), C-09 (re-checked by `check_contrast`) |
| D2 | `build.py`: CSP `connect-src 'self'` (was `'none'`), with the reason in place | C-18, C-19; D-61 |
| D3 | Workflows: every third-party action pinned by commit SHA with the version as a comment; `codeql.yml` added (python, actions), itself pinned | supply-chain hygiene; Dependabot github-actions ecosystem keeps the SHAs current |
| D4 | Tests for D1 and D2 | doctrine rule 14 |
| D5 | D-61 in DEFECTS; decisions 5.3.1 to 5.3.4; CHANGELOG [Unreleased] | C-31 |

## 3. Requirements

- No inline script, no CSP hash: C-18 stands (decision 5.3.4 records why C-02 is not pursued).
- `test_no_third_party_resources_load` and every existing gate still pass.

## 4. Out of scope

The LCP lever (5.3.4). Screen-reader passes (owner-run, A4.9). Hosting headers (A4.1).

## 5. Exit checklist, evidenced

- [x] Six gates exit 0 after the change (run by the builder 2026-08-22).
- [x] Both new tests pass; the CSP test's negative control (a policy carrying `'unsafe-inline'`) refuses.
- [ ] `measure-live` dispatched after deploy; result read back from `data/generated/audit.json` and reported.
- [x] Owner's eye-check: **waived by the owner's ruling of 2026-08-22** for this batch. Recorded as a deviation, not absorbed.

## 6. Outcome

Written after the measurement run; see the session report and DECISIONS 5.3.x.
