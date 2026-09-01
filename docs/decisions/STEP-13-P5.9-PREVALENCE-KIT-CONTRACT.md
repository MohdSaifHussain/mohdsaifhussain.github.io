# STEP-13: P5.9 — prevalence-kit added, with the repository's own figure

**Project:** mohdsaifhussain.github.io | **Phase:** P5.9 | **Date:** 2026-09-01
**Status:** Open.
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
| D7 | DECISIONS 5.9.1 to 5.9.4; CHANGELOG `[Unreleased]`; `_status` amended to name `figure` as the second permitted figure kind | C-31 |

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

## 5. Exit checklist

- [ ] Six local checks exit 0.
- [ ] D5's tests pass, and the coordinate test refuses when a coordinate is altered.
- [ ] Figure read by eye in dark, light, high contrast and forced colours.
- [ ] Figure read by eye at all eight viewports in the §3 ladder.
- [ ] Owner's go before push; `measure-live` dispatched after deploy and read.

## 6. Declared deviations from "recolour only"

Both are additions required by §3's fourth requirement, and neither moves a
datum:

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

_Open._
