# Changelog

All notable changes to this site are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and
this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Every figure below is taken from the committed record** — the defect log, the
decision log, the phase contracts, and `data/generated/audit.json` as written by
CI. Nothing here is rounded and nothing is claimed that is not measured
somewhere in this repository. Where a condition is unmet it says so.

## [Unreleased]

### Added

- **finding-bridge**, the seventh project entry and fourth flagship, every field
  quoted from its own README at origin/master `41a33ed`, anchored to release
  v1.0.0 on the REPO-STATED basis (CU-5).
- **Switchyard**, the sixth project entry, sourced from its own README and
  showcase at v1.0.0; **TS-Sentry** re-sourced to its README and CI log.
  A fourth metrics basis, **REPO-STATED**, defined and guarded (CU-1, CU-4).
- Each project card states its own basis in its own sentence; the build
  refuses a basis it cannot explain (P5.1, D-60).
- CodeQL on the build tooling and the workflows; every action pinned by
  commit SHA (P5.3).

### Changed

- The footer's `VISITS —` is retired; A4.4 resolved (P5.2).
- The three small mono type steps rise to 12px on viewports at or below
  900px, for Lighthouse's mobile legibility line; desktop unchanged (P5.3).
- CSP `connect-src` is `'self'` rather than `'none'`: Lighthouse's robots.txt
  audit fetches from inside the page and was failing on every run under
  `'none'` (D-61). No origin other than this one may be contacted.

### Fixed

- `tools/fetch_stats.py` assumed every GitHub link was a repo root (CU-3).

### Measured

After these changes, `measure-live` run 32575042812 (2026-08-22): Lighthouse
**100 / 100 / 100 / 100** worst median across both profiles, LCP 1.52 s,
CLS 0.000, 147,557 B, 0 axe violations, 0 validator errors. C-01 MET.

### Declared, unchanged

- **C-02** LCP 1.53 s against 1.5 s stays declared: the one lever left, an
  inline head script under a CSP hash, is forbidden by C-18, and the
  render-blocking theme script is ruling 4.2.7's accepted cost (5.3.4).

## [1.1.0] — 2026-08-10

### Added

- **Signature motion.** The declared animation ledger grows from four entries to
  six by recorded ruling, never silently (C-12).
  - **A3.5** — cross-document view transition, a vertical "ledger-turn" at
    250 ms, site-wide. The header and footer persist as their own snapshot
    groups while `main` turns out and in. Native CSS `@view-transition`: no
    JavaScript and no library (C-19). Duration is driven by `--motion-vt` so the
    single reduced-motion lever reaches it.
  - **A3.6** — scroll-driven reveal on the Experience register, scrubbed to
    scroll position rather than to a clock, `/experience/` only. CSS
    `animation-timeline: view()`: no scroll listeners (C-14, C-19). Its duration
    is published as `scrubbed`; no millisecond value is invented for it.
- **Light mode**, closing reading R-11 and limitation A4.8 — the last declared
  v1.1 limitation on the register.
  - Reachable by `prefers-color-scheme` and by a manual toggle; the manual
    choice wins. **Dark remains the default; light is the guest mode.**
  - The palette is *derived*, not invented: the light ink is the dark background
    inverted, and `--body`, `--bright` and `--dim` mirror their dark measured
    ratios. The derivation rule and solved values are published in
    `docs/decisions/STEP-09-P4.2-LIGHT-DERIVATION.md`.
  - Every hex appears exactly once; the semantic tokens are pointers remapped
    per theme, so the two palettes cannot drift.
  - **The visible cost is the accent.** No amber survives a light ground at any
    WCAG-meaningful ratio — `#e8b64c` has relative luminance 0.511 against an
    AA ceiling of 0.183 — so light mode carries a bronze `#695222` at 7.05:1.
  - The theme toggle is the site's first `<button>`: keyboard reachable, with
    the site's accent focus ring, state in `aria-pressed`, and instant. The
    animation ledger did not grow to accommodate it.
  - Persistence is **per-visit** via `sessionStorage` — one key, the theme word
    only, cleared with the tab — applied before first paint. No cookie is set.
- **CI-measured live counts**, implementing defect D-02's recorded upgrade path
  (DECISIONS 3.1.3a). Each source repository's CI publishes a `stats.json`
  counted from the JUnit report of the run that executed its tests, and this
  site consumes it.
  - `delivery-engine` 419 → **453 tests**, `analystkit` 53 → **75**,
    `opskit` **18** (unchanged, and now measured rather than asserted).
  - TS-Sentry remains owner-measured at 1,230 tests, unchanged.
  - The label is "tests", not "unit tests": the measurement counts what pytest
    executed and does not establish that every one is a unit test.
- **/audit gains A5** — every contrast pair, in both themes, recomputed from
  `tokens.css` by the WCAG 2.2 relative-luminance formula on every measurement.
- **Dependency automation** — Dependabot for `pip` and `github-actions`, weekly,
  with auto-merge for patch and minor updates strictly conditional on the full
  gate wall passing. Major updates never auto-merge.

### Changed

- **The measurement protocol is now applied to every figure it claims to
  govern.** LCP, CLS and the transfer figure took the worst *single run* while
  /audit published "median of 3 runs per page per profile … the WORST median".
  Only the Lighthouse category scores had ever implemented it. Corrected to the
  pre-registered method (defect D-52).
- **Version anchors prefer the newest semver tag** over the latest release when
  the two disagree; a tag is the stronger version claim and a release is
  packaging. Linked by tree URL, since `releases/tag/…` 404s for a tag with no
  release.
- **Scheduled jobs now publish what they commit.** `refresh-stats` and
  `measure-live` dispatch a deploy explicitly, because a push made with the
  default `GITHUB_TOKEN` does not trigger other workflows (D-45, D-46, D-47).

### Fixed

Fourteen defects, D-46 through D-59. By how each was found:

| Found by | Count | Defects |
|---|---|---|
| Reading the code or record against its claims | 6 | D-46, D-47, D-48, D-54, D-55, D-57 |
| Running it — a gate, build, audit, sabotage or measurement refusing | 7 | D-49, D-50, D-51, D-52, D-53, D-56, D-58 |
| The owner walking the live site | 1 | D-59 |

The ones worth naming:

- **D-48** — nine of fourteen cells on /audit read "— AT DEPLOY" for the whole
  of v1.0.0 under a footnote promising CI measured them. Eight had no writer
  anywhere in the repository.
- **D-50** — the reduced-motion gate was blind to every animation it existed to
  police. Deleting the lever left A3.5 running at full duration for a visitor
  who had asked for reduced motion, while the checker printed "motion is
  switchable off" and exited 0. That sabotage is now its permanent control.
- **D-51** — scrubbed opacity on text is a *resting* state, not a transient
  frame; `--dim` fell below AA. Caught by the browser audit refusing the deploy.
- **D-52** — the published LCP swung 1.65 → 2.25 → 2.28 → 2.32 s across four
  measurements of a barely-changing site, while the worst median sat at
  1.53–1.56 s. It nearly triggered a revert of work whose true cost was 0.01 s.
- **D-58** — the theme toggle shifted every page as it appeared: CLS 0.000 →
  0.043. Only the measurement could have caught it.
- **D-59** — the decision said per-visit; the implementation delivered per-page.
  No condition encoded the difference, so no gate could have caught it.

### Measured

Median of 3 runs per page per profile, both profiles, against the published
origin. 30 reports.

| Metric | v1.0.0 | v1.1.0 | Condition |
|---|---|---|---|
| Lighthouse, worst median | 100 / 100 / 96 / 92 | 100 / 100 / 96 / 92 | **C-01 UNMET, declared** |
| LCP, worst median | 1.53 s *(published 1.65 s; see Erratum 2)* | **1.53 s** | **C-02 UNMET, declared** |
| CLS, worst median | 0.000 | **0.000** | C-02 CLS MET |
| Home first-view transfer | 143,035 B | 146,967 B | C-03 MET |
| axe | 0 violations | 0 violations, **5 pages × 2 themes** | C-06 MET |
| W3C validator | 0 errors | 0 errors | C-23 MET |

**Erratum 2**, filed against STEP-07 and the `v1.0.0` tag message: the released
LCP figure of 1.65 s was a worst *single run*, not the worst median its own
published protocol specified. Under that protocol the release measured 1.53 s.
The direction of the error was pessimistic and the method was non-conformant;
the original text is left intact.

## [1.0.0] — 2026-08-06

The first public release. A governed, audited personal portfolio built across
five phases, each closed against the frozen charter's 36 conditions with
evidence.

### Added

- Five pages rendered from data files — no HTML is edited to change content.
- `/audit`, the site's own report card: measured standards, charter checks, the
  shipped animation ledger, and the limitations it declares rather than hides.
- Four declared animations (A3.1–A3.4), a strict CSP delivered by meta, and
  self-hosted subset fonts with zero third-party resources.
- A test suite and six local gates that refuse the build rather than publish
  bad output.

### Measured

100 / 100 / 96 / 92 Lighthouse, LCP 1.65 s as published (1.53 s under the
protocol; see Erratum 2), CLS 0.000, 143,035 B, 0 axe violations, 0 validator
errors, contrast AA in full with 7:1 everywhere except `--dim` at 5.78:1.

### Declared unmet

- **C-01** — best-practices 96 and SEO 92, with their causes stated on /audit.
- **C-02** — LCP against a 1.5 s target.
- **C-08** — met in part: the screen-reader pass covers Home only.

### Notes

45 defects logged to that point, including four cases where a green signal meant
nothing: fabricated scores reaching the live page, a desktop run erasing the
mobile run, the site shipping with no stylesheet while 46 tests passed, and a
test written to catch that which could not itself fail.

[1.1.0]: https://github.com/MohdSaifHussain/mohdsaifhussain.github.io/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/MohdSaifHussain/mohdsaifhussain.github.io/releases/tag/v1.0.0
