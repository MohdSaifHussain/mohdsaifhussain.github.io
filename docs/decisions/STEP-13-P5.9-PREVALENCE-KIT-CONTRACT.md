# STEP-13: P5.9 — prevalence-kit added, with the repository's own figure

**Project:** mohdsaifhussain.github.io | **Phase:** P5.9 | **Date:** 2026-09-01
**Status:** **Closed 2026-09-01.** Exit criterion met, with one part declared rather than claimed: the figure was not read by eye under forced colours (§5, §7). Owner's go given for the push; deployed and measured against the published origin.
**Tier:** FULL, ruled by the owner 2026-09-01. It publishes to the live public site and it edits a template, which SOP §1 defines as a design change rather than a content update. Every prior template-touching phase (P5.4 to P5.8) ran FULL.
**Verified on mobile:** required, per the owner's ruling of 2026-08-22. The owner additionally directed on 2026-09-01 that the result be checked "on all type of devices and screens", which widens the mobile check to a stated ladder of viewports (§3).
**Depends on:** P5.8 closed.

## 1. Objective

Add `prevalence-kit` to `/projects/` as the eighth entry and fifth flagship, with
its content taken from its own README and its figure taken from the one image
that README publishes.

**Exit criterion:** the entry renders on `/projects/` and on the home flagship
list; its figure renders legibly and correctly in all four display modes (dark,
light, high contrast, forced colours) and at every viewport in the §3 ladder;
the six local checks exit 0; and after deploy, `measure-live` reports no new
axe violation and no new validator error.

## 2. Deliverables

| ID | Deliverable | Governing standard |
|---|---|---|
| D1 | `data/projects.json`: the `prevalence-kit` entry, `metrics_basis: repo-stated`, `flagship: true`, every prose field quoted from the README at `origin/main 6155194` with markup dropped and no word changed | CU-5 precedent (owner's direction 2026-08-25); CU-1 (the REPO-STATED definition) |
| D2 | `templates/figures/prevalence-kit-coverage.svg.j2`: the README's `demo/coverage_curve.svg`, recoloured to tokens and otherwise unchanged | contract 3.2 (no colour literal outside `tokens.css`); owner's ruling Q5, 2026-09-01 |
| D3 | `templates/projects.html.j2`: a third figure kind, `figure`, beside the existing `diagram` and `outcome` | C-34 (no HTML edited to change content; this adds a kind, not a value) |
| D4 | `static/css/site.css`: the `.chart` block, tokens only, no animation | contract 3.2; C-09; C-15 |
| D5 | Tests: the figure is declared and cited, carries no colour literal, and every data coordinate matches the source SVG | doctrine rule 14 |
| D6 | `data/generated/github.json` refreshed so the entry anchors | SOP §1 step 3; `PUSH_DATE_MISSING` |
| D7 | DECISIONS 5.9.1 to 5.9.4 (**landed as 5.9.1 to 5.9.12; reconciled in §7**); CHANGELOG `[Unreleased]`; `_status` amended to name `figure` as the second permitted figure kind | C-31 |

## 3. Requirements

- **The figure must be inline SVG, not a served file.** An `<img src="*.svg">` is a
  separate document and cannot resolve the page's custom properties, so served as
  a file it can never theme and would render as a white slab in dark mode. Inline
  is the only construction that satisfies the owner's condition of 2026-09-01
  that it work in light, dark and high contrast.
- **Recolour only.** Every coordinate, every path, every data point and every word
  of the source SVG is carried across unchanged. What changes is the eight colour
  values, the font family, and the two items named as deviations in §6.
- **No new animation.** The chart carries its own class, not `.diagram`, so
  `diagram.js` never arms it and A3.7's declared list is untouched.
  `check_animations.py` must stay green in both directions.
- **The two series must be distinguishable without colour.** Under
  `forced-colors: active` the browser repaints both series to `CanvasText`, so a
  hue-only distinction is no distinction. WCAG 2.2 SC 1.4.1.
  <https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html>
- **Viewport ladder** (the owner's "all type of devices and screens", made
  checkable): 360x780, 390x844, 414x896, 768x1024, 1024x768, 1280x800, 1440x900,
  1920x1080. The figure must be readable, must not clip its own text, and must
  not make the page scroll horizontally at any of them.

## 4. Out of scope

An architecture diagram for this entry: the owner ruled 2026-09-01 that the
image replaces it. Any change to the six existing diagrams. Any change to the
other seven entries. Widening the C-27 em-dash gate (still CU-2's open question).

## 5. Exit checklist, evidenced

- [x] **Six local checks exit 0**, re-run after every change including the last
      (build, pytest, c33, content, animations, contrast), plus
      `gen_chart.py --selftest` exit 0 and `fetch_stats.py --verify-links` exit 0.
      Exit codes read directly, never inferred from the last line of output (D-39).
- [x] **D5's tests pass, and the coordinate test refuses when a coordinate is
      altered.** The negative control did more than pass: it found that the
      test's own attribute pattern matched no name containing a digit, so
      `x1`/`y1`/`cx`/`cy` were absent from the comparison and the check was
      passing vacuously (5.9.8). Fixed, then re-run.
- [~] **Figure read by eye in dark, light, high contrast — and NOT under forced
      colours.** Dark, light and both high-contrast palettes were rendered,
      screenshotted and measured: both series clear 10:1 against the background
      in every mode, every text pair clears 7:1. Forced colours could not be
      emulated from this session and was **not** eye-checked. What exists in its
      place is an argument and a test, not an observation: the Wilson dash is a
      non-colour channel and survives any repaint, and `.c-grid` is given
      `GrayText` under `forced-colors: active`. Declared, not claimed.
- [x] **Figure read by eye at all eight viewports in the §3 ladder.** Measured
      through same-origin iframes, because resizing the OS window left
      `innerWidth` pinned at 1536 and produced identical numbers at every size —
      a false pass that would have been easy to accept. Result at 360x780,
      390x844, 414x896, 768x1024, 1024x768, 1280x800, 1440x900 and 1920x1080:
      zero clipped text, no horizontal page scroll, the figure scrolling inside
      its own frame below 1024 as designed.
- [x] **Owner's go before push; `measure-live` dispatched after deploy and read.**
      Owner ruled the tier, the figure treatment, the legend placement and the
      opening text, and gave the go. Deploy passed the axe wall; measured twice
      against the published origin (§7).

## 6. Declared deviations from "recolour only"

Four, not the two this section was drafted with. Numbers 1 and 2 were declared
before any measurement; 3 was named as a possibility and then measured; 4 was
not foreseen at all and came from the owner's eye. None moves a datum. The
count is corrected here rather than in the outcome, so the contract shows what
it actually permitted:

1. **The white ground rect is deleted** rather than recoloured. Recolouring it to
   `var(--bg)` would paint an opaque slab that defeats the high-contrast and
   forced-colours layers; deleting it lets the page's own ground show through,
   which is what every other figure on this site does.
2. **The Wilson series is dashed** (`stroke-dasharray`), on its path and on its
   legend swatch. This is the redundant, non-colour channel SC 1.4.1 requires.
   The dash pattern is chosen distinct from the nominal-0.95 reference line's
   existing `6 4` so the two cannot be confused.

3. **The four prose lines are lifted out of the drawing** and rendered as HTML
   beside it, and the viewBox is cropped to the geometry that remains. Foreseen
   as a possibility before measuring (the paragraph this replaces said "may
   follow from measurement and is not yet claimed"), then measured: in the
   source's Georgia one line overruns the 760-unit box, in this site's wider
   monospace three do. An SVG clips to its viewport, so an overrun is lost text.
   The remedy the earlier paragraph guessed at — widening the viewBox — was
   rejected once measured, because fitting the longest line needs about 1,216
   units and would flatten the plot into a strip.

4. **The legend moves out of the plot** onto one row beneath the axis, on the
   owner's ruling of 2026-09-01 after they confirmed the overlap by eye
   (decision 5.9.10). Not foreseen: the Clopper-Pearson path crosses its own
   label in the source drawing too, and this site's monospace widened the
   crossing from 14 sampled points to 25. Annotation only; no datum moves.

## 7. Outcome

**Delivered.** prevalence-kit renders as the eighth entry and fifth flagship on
`/projects/` and on the home flagship list, carrying the one figure its README
publishes. `figure` now exists beside `diagram` and `outcome` as a third figure
kind, and `_status` states the widened invariant — a live entry carries one of
the two, no longer a diagram specifically — with
`test_every_live_entry_carries_a_figure_or_a_diagram` holding it.

**Measured against the published origin**, twice, both published exactly as
measured (SOP §5; no run was repeated to obtain a better figure):

| | after the first push | after the text change |
|---|---|---|
| Lighthouse | 100 / 100 / 100 / 100 | **97** / 100 / 100 / 100 |
| axe | 0 violations | 0 violations |
| W3C validator | 0 errors | 0 errors |
| CLS | 0.000 | 0.000 |
| LCP (worst median) | 1.65 s | 1.79 s |
| Transfer | 149,832 B | 149,863 B |

**On the performance score, stated against the right baseline.** The builder
first reported this as an LCP regression by comparing with P5.3 (1.52 s,
2026-08-22), which was not the preceding measurement. The measurement
immediately before this phase, 2026-08-31, read **99 / 100 / 100 / 100 at LCP
1.80 s**. So LCP went 1.80 s to 1.79 s and did not move; the performance score
went 99 to 97. This site had already scored 99 twice before this phase, and the
same build measured 1.39 s and 1.55 s fifteen minutes apart on 2026-08-27, a
0.16 s spread on near-identical bytes. This phase added about 1 KB. Two points
on one run against a metric with that spread does not attribute, and no
attribution is claimed here in either direction. The correction is recorded
beside the original because it moved toward a less flattering account of the
builder's own reporting, not of the site.

**Deviations from the contract.** Four rather than the two §6 was drafted with,
and §6 now says so with which were foreseen and which were not. The one that
matters: §3 required "recolour only", and the legend move (deviation 4) is a
geometry change to annotation. It is exempted by name in the coordinate test —
pulled out of both sides and counted at exactly four — rather than by relaxing
what that test checks for everything else.

**Deliverable list reconciled against what exists.** D7 promised "DECISIONS
5.9.1 to 5.9.4"; eleven landed, 5.9.1 to 5.9.11, because the review stop and
the owner's two later rulings produced findings the contract could not have
named in advance. Raised here rather than left as a contract that quietly
describes different work from the work that happened.

**Not part of this phase, done alongside it:** the codeql-action bump to v4.37.9
(commit "ci: bump both codeql-action pins"). Dependabot's two PRs each bumped
one half of an action pair that must match, so both were red; one commit bumping
both fixed it, and CodeQL has run green on `main` since. Recorded here only so
the phase's commit range is not misread as containing it.

### Carried obligations

| Obligation | Owner | Status |
|---|---|---|
| **C-20 and the PyPI link (5.9.7).** The gate refused `pypi.org`; the link was dropped and the fact kept in `verified_metrics`. Whether the allowlist widens is a charter amendment | A later phase, on the owner's ruling | **Unmet, named.** Not a defect: the gate was right and was not bypassed |
| **`build.py`'s colour gate does not recurse (5.9.9).** `TPL.glob("*.j2")` never sees `templates/diagrams/` or `templates/figures/`. No literal is present in either today | A later phase, in the manner of CU-2 | **Unmet, named.** Closed for `figures/` by test; `build.py` itself unchanged |
| **C-02, LCP ≤ 1.5 s.** Declared UNMET since P5.3 and still declared, now at 1.79 s | Deferred by the owner's ruling of 2026-09-01 (decision 5.9.12) | **Unmet, declared, deliberately not pursued** |
| **Forced-colours eye-check.** Not performed; §5 records what stands in its place | A later phase, or the owner on a Windows high-contrast session | **Unmet, named** |
