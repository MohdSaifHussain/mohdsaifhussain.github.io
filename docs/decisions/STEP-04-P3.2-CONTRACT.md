# STEP-04 (P3.2): Pages wired from data, responsive derivation, metadata

**Project:** mohdsaifhussain.github.io | **Phase:** P3.2, 2 of 5 | **Date:** 2026-08-06
**Status:** Specified, not started
**Tier:** FULL

**Depends on:**
- **STEP-03 (P3.1), CLOSED** — specifically: the `build.py` gate architecture (12 reason codes, pure functions over text), `tokens.css` as the sole source of colour/type/spacing, the `_mark()` shared SVG definition, the committed woff2 subsets, and the deterministic cross-platform build (hash `9ba23fb8167a4e2a`).
- STEP-01-CHARTER v1.0 **+ Amendments 1 and 2** (C-33 scoped to contact-capable addresses; exemptions enumerated).
- STEP-02-HANDOFF §3 (page layouts), §4 (component specs), §1 (tokens).
- DECISIONS 3.1.3 / 3.1.3a / 3.1.3b — the D-02 ruling this phase implements.

**Numbering:** `STEP-NN` for these files, `P3.x` for build phases, charter "Phase 3" for the whole build (declared STEP-03).

**Standing rule:** every implementation follows the top applicable standard for what is being built; each requirement names its governing standard. If a standard is ambiguous, stop and ask rather than guess.

---

## 1. Objective

Turn the P3.1 skeleton into the five real pages of handoff §3, every value rendered from `data/*.json`, with GitHub-derived stats version-anchored and evidence-linked per the D-02 ruling, complete metadata, and a mobile derivation that does not exist in the frozen handoff and therefore needs the director's explicit approval.

**Exit criterion:** all five pages render their full committed layouts from data with zero hand-entered values; `check_c33.py` and `check_content.py` both refuse their poisoned fixtures and accept the real repo; and the site has no horizontal overflow at 375 px.

## 2. Deliverables

Ordered so the load-bearing work precedes the surface, and so **O-9 is discharged early** (D2).

| ID | Deliverable | Governing standard(s) |
|---|---|---|
| D1 | Home: identity section, flagship ledger rows (grid 120/1fr/1fr/220), truth strip | Handoff §3, §4; C-34 |
| **D2** | **Projects: `scroll-snap` case slider, cards with `01 / 05` position, ✓ verified rows and TS-Sentry's pending ✗** | Handoff §3 (3a), §4; C-14; **discharges O-9** |
| D3 | Experience: NO./PERIOD/ROLE/RECEIPTS table, education line, PDF button | Handoff §3 (3b); C-29 |
| D4 | Certifications: `00 / 00` empty state, tile-anatomy specimen, tile grid when populated | Handoff §3 (3c), §4 |
| D5 | /audit: A1 standards, A2 charter checks, A3 shipped animations; "— AT DEPLOY" when `audit.json` is absent | Handoff §3 (3d); C-30; C-35 |
| D6 | `tools/fetch_stats.py` → `data/generated/github.json`: per-repo release tag or commit SHA, with an "as of" stamp | **C-35**; GitHub REST API docs, cited by URL |
| D7 | `projects.json` promise strings rewritten per D-02 — **new text, triggers O-3** | C-27; DECISIONS 3.1.3 |
| D8 | `tools/check_c33.py` — enumerated allowlist, ISO-8601 exclusion, PDF text scan | **C-33 + Amendments 1 and 2**; defects D-11, D-17 |
| D9 | `tools/check_content.py` — em-dash scope, no count literals, no inline style/script | C-27 (em-dash rule), C-34; defects D-07, D-08 |
| D10 | OG image + favicon set + web manifest, generated from tokens | C-25; defect D-09 |
| D11 | Metadata: per-page title/description, OG + Twitter, canonical, `sitemap.xml`, `robots.txt` | **C-25**; WHATWG HTML |
| D12 | JSON-LD: `Person` on home, `SoftwareSourceCode` per project | **C-26**; schema.org |
| D13 | Semantic landmark and heading-level audit across all five pages | **C-24**; WAI-ARIA 1.2 |
| D14 | **Responsive derivation** — slider, table and grids restack; type scale steps down; nav wraps; no horizontal overflow | Handoff §1 tokens; C-13; defect D-06 |
| D15 | Test suite extended, one test per new gate behaviour | Policy approved at P3.1 review stop |

## 3. Requirements

- **3.1** No value a script could compute is typed by hand. Every count, position indicator (`01 / 05`), year span and entry total renders from data. *Standard: C-34; defect D-07.*
- **3.2** **`build.py` never reaches the network.** `fetch_stats.py` is a separate, explicitly-run tool writing a committed snapshot; the build reads only that snapshot. A build that fetches is neither deterministic nor reproducible offline, and P3.1's cross-platform hash guarantee would be lost. *Standard: C-35; STEP-03 requirement 3.7.*
- **3.3** Every displayed GitHub-derived count carries **both** a version anchor and an evidence link to its source. A count with only one of the two is a build failure. *Standard: C-27, C-35; DECISIONS 3.1.3.*
- **3.4** `check_c33.py` implements the Amendment 2 allowlist **by enumeration**, with three controls: a routable-looking address must trip it; `noreply@` at an *unlisted* domain must **also** trip it (this is what proves enumeration rather than pattern-matching); a fixture of ISO-8601 dates must not trip it. *Standard: C-33 + Amendments 1–2; defects D-11, D-17.*
- **3.5** The C-33 scan covers the repo **and** the extracted text of the web-resume PDF. *Standard: C-33.*
- **3.6** The em-dash ban is enforced on exactly `experience.json`, the rendered Experience page, and the PDF — not site-wide, which the frozen h1 and the charter's own colophon make impossible. *Standard: C-27; defect D-08.*
- **3.7** No new animation. Handoff §5 closes the list at three, and none of them ships until P3.3. Mobile navigation wraps by CSS; a disclosure menu would be a fourth animation. *Standard: handoff §5; C-12; defect D-06.*
- **3.8** Zero inline style attributes and zero inline script bodies continue to hold, as gated in P3.1. *Standard: C-18.*
- **3.9** `_status` in `projects.json` is not moved out of "pending re-verification" by me. Only the director's recorded re-verification discharges O-3. *Standard: C-27.*
- **3.10** All close commands PowerShell 5.1-safe: `;` and `if ($?)`, never `&&`.

## 4. Out of scope

The three animations, reduced-motion kill switch, IST clock (P3.3) · CSP meta, keyboard/NVDA/contrast passes (P3.4) · Lighthouse/axe/validator wiring, real audit scores, SOP.md, the tag (P3.5) · GoatCounter (ruled out of v1.0.0 by D-03) · the v1.1 `stats.json` path (DECISIONS 3.1.3a).

**Not claimed this phase:** C-01, C-02, C-03 — no measurement tooling until P3.5.

## 4a. Review stop

**Halt after D1–D9, before D10–D14.**

The data binding, the stats pipeline and the two checkers are load-bearing: metadata, generated images and the responsive layer all sit on top of them, and a defect in the binding found after the responsive work is found too late. At the stop I will:

1. Prove by quoting exact lines that every rendered count comes from `len(data)` or a snapshot field, never a literal.
2. **Report `MARK_DRIFT`'s first coverage of real dual-mark output** (O-9), naming the page and the marks — P3.1's honest limit was that the gate could not fire on real pages.
3. Show the three `check_c33.py` controls firing, including the unlisted-`noreply@` case.
4. **Present the D-02-rewritten `projects.json` text for the director's re-verification (O-3).** C-27 cannot report MET until that is recorded.

## 5. Exit checklist

- [ ] All five pages render their committed layouts; no value hand-entered
- [ ] **Negative:** `check_c33.py --selftest` exits non-zero on a routable address **and** on `noreply@` at an unlisted domain, with distinct reason codes
- [ ] **Positive:** `check_c33.py` exits 0 on the real repo, and the ISO-date fixture does not trip it
- [ ] **Negative:** `check_content.py --selftest` refuses an em-dash in resume-derived text and a hardcoded count
- [ ] **Positive:** `check_content.py` exits 0 on the real repo
- [ ] `MARK_DRIFT` demonstrated covering a real page carrying both ✓ and ✗ (O-9)
- [ ] Every GitHub-derived count shows an anchor and an evidence link; a count missing either fails the build
- [ ] `github.json` carries a visible "as of" stamp, and the build never fetched
- [ ] Nu validator: 0 errors on all five pages; one `h1` per page; landmarks present
- [ ] JSON-LD validates clean
- [ ] **No horizontal overflow at 375 px on any page** — director checks by eye
- [ ] Director's approval of the responsive derivation (O-6)
- [ ] **Director's re-verification of the D-02-rewritten fields recorded (O-3)**
- [ ] Build remains deterministic and cross-platform

## 6. Obligations entering P3.2

| # | Obligation | Owner | State |
|---|---|---|---|
| O-1 | TS-Sentry metrics | owner → P3.5 | Open; renders honest ✗ (and is the ✗ that discharges O-9) |
| O-2 | Certifications entries | owner → P3.5 | Open; `00 / 00` empty state |
| **O-3** | **C-27 re-verification of D-02-rewritten fields** | **director → this phase's review stop** | **Open; gates C-27** |
| O-6 | Responsive derivation approved | director → this phase's close | Open |
| **O-9** | **`MARK_DRIFT` first real dual-mark coverage** | **P3.2 / D2** | **Open; discharged early by design** |
| O-8 | `font-display: swap` measured | P3.5 | Carried |

## 7. Numbered questions — for the director before building

**Q1 — How does the stats snapshot stay fresh?** Charter §6A mentions a scheduled Action for C-35 refresh.
- **(a) Scheduled Action re-fetches and commits `github.json` back (recommended).** Repo stays the single source of truth, `build.py` stays hermetic, and the commit is authored by `github-actions[bot]@users.noreply.github.com` — already exempt under Amendment 1 item (1), so no new amendment is needed. Cost: automated commits land without human review.
- (b) Fetch at CI build time, never commit. No bot commits, but CI output then differs from local output and the cross-platform determinism guarantee from P3.1 is lost.
- (c) Manual refresh only — you run `fetch_stats.py` and commit. Maximum control, but the "as of" stamp goes stale silently between releases.

**Q2 — Should a stale snapshot ever fail the build?** The page always displays its "as of" date honestly regardless.
- **(a) Never fail; display honestly (recommended).** A stale date is information, not a defect, and a hard failure would block an unrelated content edit.
- (b) Warn above a threshold you set. (c) Fail the build above a threshold.

**Q3 — How should C-05 report?** The committed direction is pure-type: no content images ship. C-05's substance (modern formats, explicit sizing, lazy-loading below the fold) has nothing to apply to. The generated OG image is metadata, never rendered in-page.
- **(a) Report C-05 as MET-not-applicable on /audit, with that sentence spelled out (recommended).** Honest: the condition is satisfied because nothing it governs exists, which is not the same as passing a test.
- (b) Report plain MET. Reads as though an image pipeline was audited. (c) Report N/A with no MET claim.

## 8. Honest limits entering this phase

- C-27 cannot report MET until O-3 is discharged by the director, no matter how much of this phase completes.
- The responsive derivation is **new design not present in the frozen handoff**. It is derived from handoff §1 tokens, but it is my derivation and needs approval on its own terms (O-6).
- P3.1's honest limit stands until D2 lands: `MARK_DRIFT` has never fired on real output.
- The Nu validator and JSON-LD checks in this phase are run manually; wiring them into CI is P3.5 scope.
