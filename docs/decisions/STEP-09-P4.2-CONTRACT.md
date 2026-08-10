# STEP-09: P4.2 — Light mode (closing R-11 / A4.8)

**Project:** mohdsaifhussain.github.io | **Phase:** P4.2 | **Date:** 2026-08-10
**Status:** **Closed 2026-08-10.** D1-D7 shipped. Light mode live behind a
toggle; dark remains the default. Six defects found, five by machinery refusing
or by measurement, one by the owner walking the site. Palette approved
provisionally on the measured table, then **BINDING** on the owner's live eye
check in both themes with real fonts.
**Tier:** FULL — public site, a deploy, and a visible change to the first thing
a visitor sees.
**Depends on:** STEP-08 (P4.1) closed — the six-entry A3 ledger, and the
`SCRUBBED_CONTRAST_RISK` / `MOTION_NOT_REDUCED` machinery this phase had to keep
green without changing the ledger.

**Authority:** charter §5 — *"Palette: monochrome (near-black / off-white) plus
exactly one accent color. Dark-first; light mode optional later, never at the
cost of C-09."* Closing reading R-11 and published limitation A4.8.

**Recorded deviation on process.** This contract was written and approved
BEFORE the build, but as a plan file outside the repository. It is transcribed
here at close so the phase is reconstructable from the repository alone, which
is the standing expectation for this project. The contract was binding from
approval; only its location changed.

## 1. Objective

Ship a light theme derived from the existing palette under the contrast
machinery, reachable by system preference and by a manual toggle, without
costing any measured guarantee the dark theme already holds.

**Exit criterion:** the owner toggles against their system preference, walks all
five pages, and the choice holds — with every pair measured in both themes on
/audit and A4.8 closed in the register.

## 2. Deliverables

| ID | Deliverable | Governing standard |
|---|---|---|
| D1 | `check_contrast.py` theme-aware: both palettes, three constraints, `--json-out` | C-09 |
| D2 | The light palette in `tokens.css`, derived and published | C-09, charter §5 |
| **—** | **REVIEW STOP** — both palettes on the live-page layouts, for the owner's eye | — |
| D3 | The theme toggle: first `<button>`, keyboard and focus parity, instant | C-07, C-11, C-18, C-21 |
| D4 | Interaction-QA row 14, and the limit that prior `O` marks are dark-only | handoff §6 |
| D5 | Browser audit exercising BOTH themes with a rendered-background witness | C-06 |
| D6 | /audit: A5 per-token table both themes, A4.8 struck, persistence declared | C-30, C-35 |
| D7 | Standing measurement; LCP ≤ 1.55 s, CLS 0.000, transfer in budget | C-01, C-02 |

## 3. Requirements

- **3.1** AA in full, at the size each pair is used, in both themes.
- **3.2** ≥7:1 in light wherever the dark theme achieves it.
- **3.3** `--dim`'s shortfall may not deepen below its dark 5.78:1.
- **3.4** Per-token measured ratios for both themes published on /audit.
- **3.5** `prefers-color-scheme` respected, plus a manual toggle; the manual
  choice wins.
- **3.6** The toggle is instant. The A3 ledger stays at six and
  `check_animations` stays green with no list change.
- **3.7** Persistence complies with C-21, with the condition text cited before
  implementing.
- **3.8** axe zero violations on every page **in each theme**, with the job
  proving it exercised both rather than assuming the second.
- **3.9** No second stylesheet download; light ships as custom-property
  overrides.
- **3.10** No regression: LCP worst-median ≤ 1.55 s, CLS 0.000.

## 4. Out of scope

- Any change to the A3 ledger. Light mode adds no animation.
- The dark palette. Unchanged, to the hex.
- Persisting a theme ACROSS visits. Ruled per-visit; see A4.10.

## 4a. Review stop

Halt after **D2**, before **D3**: the palette is the load-bearing decision and
every later deliverable assumes it. Presented as a labelled facsimile, since the
builder has no browser — with the binding verdict deferred to the live site.

## 5. Exit checklist

- [x] Both palettes measured; all three constraints hold
      - *22 rows. AA in full; light loses no 7:1; `--dim` 5.78 → 5.79.*
- [x] The checker cannot collapse the two themes
      - *Control asserts the same pairs measure differently per theme — exactly
        what the old flat parse would have broken.*
- [x] Toggle: keyboard reach, focus ring, state announced, instant
      - *Native `<button>`; `:where(button):focus-visible` added; `aria-pressed`
        with a constant label; no transition, ledger still six.*
- [x] axe zero violations, every page, **each theme**, proven
      - *`themes exercised: dark, light`; `distinct backgrounds: rgb(13,13,12),
        rgb(250,249,246)` — the witness. `THEME_NOT_APPLIED` guards it.*
- [x] /audit publishes per-token ratios for both themes
      - *A5, derived from `check_contrast.py`, replacing a typed literal (D-55).*
- [x] A4.8 closed and struck with what closed it and the date
- [x] LCP ≤ 1.55 s, CLS 0.000
      - *1.53 s and 0.000, after D-58 was found and fixed.*
- [x] Owner's live eye check, both themes, real fonts
      - *Performed 2026-08-10. Palette BINDING.*

## 6. Outcome

**Shipped:** D1-D7, live at `0d4ed3c`. Light mode reachable by system preference
and by toggle; dark unchanged and still the default.

### Measured, under the standing protocol

| Metric | Measured | Condition |
|---|---|---|
| Lighthouse, worst median | 100 / 100 / 96 / 92 | C-01 UNMET, declared |
| LCP, worst median | **1.53 s** | C-02 UNMET, declared — ceiling held |
| CLS, worst median | **0.000** | C-02 CLS MET |
| Home first-view transfer | 146,967 B | C-03 MET |
| axe | 0 violations, 5 pages × 2 themes | C-06 MET |
| W3C validator | 0 errors | C-23 MET |
| Contrast | dark: AA met, 7:1 except `--dim` (5.78:1) · light: same (5.79:1) | C-09 MET |

### Phase close, verified

Performed personally by the owner on the live site, in both themes with the real
fonts, 2026-08-10.

| Scenario | Expected | Observed |
|---|---|---|
| Palette, both themes | bronze accent legible; rule/tint weights right | **As expected.** Bronze works; weights read right |
| Toggle affordance | reads as a control, not a nav item | **As expected.** Keyboard reach, accent ring, state unambiguous |
| Ledger-turn and scrub in light | coherent; transform/opacity only | **As expected** |
| Marks and colophon, both themes | legible | **As expected** |
| Toggle AGAINST the system preference, walk all five pages | the choice holds | **Held on every page** |
| Fresh tab from a pasted link | opens at the SYSTEM preference | **Opened dark, the system preference** — per-visit exactly as designed |
| Navigation | no flash of the wrong theme | **No flash on any navigation** |

**The row worth keeping in view:** the fresh-tab check, which the owner added
themselves. It is the only one that demonstrates a *limitation working* — the
choice deliberately not outliving the visit — and it is the difference between
persistence that was designed and persistence that merely happened.

### Defects found by running it, not by inspection

Six. Five by machinery refusing or by measurement; one by the owner.

1. **D-55** — the published contrast figure was typed, not measured.
   `write_audit.py` discarded the checker's output and wrote `5.78:1` by hand.
   Had a token changed, the gate would still have exited 0 while /audit
   published the old number forever. Found by reading the chain while planning.
2. **D-56** — `read_token("--bg")` refused the build the moment the tokens
   became pointers. The right failure at the right time: two `theme-color` metas
   now ship, where one would have left the browser chrome dark above a light
   page.
3. **D-57** — the global focus ring enumerated `a` and `span[tabindex]`, which
   covered everything only because the site contained no `<button>` at all. The
   first real control would have taken the user-agent ring.
4. **D-58** — the toggle shifted every page as it appeared. CLS 0.000 → 0.043.
   **This is D-31 exactly**, whose lesson I had applied to an element someone
   else wrote and not to my own. Only the measurement could have caught it.
5. **D-59** — the decision said per-visit; the implementation delivered
   per-page. Found by the owner walking the site — then nearly lost again when
   a follow-up observation reported the theme "stays", which the evidence
   contradicted, and the phase was held open rather than closed on it.

### Readings and deviations, recorded

- **R-16** — charter §5's "exactly one accent color" is read as one accent
  ROLE, themed. The frozen-hex reading would make §5 contradict its own
  light-mode permission.
- **R-17** — the toggle is unnumbered. The `01`–`04` + `A` scheme means *a place
  you can go*, and numbering a button would make the wayfinding scheme lie about
  what it indexes.
- **Deviation** — this contract was approved as a plan file outside the
  repository and transcribed here at close. Binding from approval; only its
  location changed.
- **Finding 2, considered and withdrawn** — darkening light text further was
  considered at the eye check and decided against. Recorded as decision 4.2.6 so
  it does not resurface.

### Obligations

**Discharged:** R-11 and A4.8, the last declared v1.1 limitation on the
register.

**New, declared:** A4.10 — the toggle remembers your choice for the visit and
forgets it when the tab closes.

**Carried, unchanged:** C-08's four screen-reader-unverified pages (A4.9);
C-36's owner SOP walkthrough; A4.7's historical commit.

### Honest limits

- **The theme toggle has no screen-reader pass.** It is the site's first
  interactive control and its `aria-pressed` semantics are asserted
  structurally, not heard. It joins A4.9 rather than narrowing it.
- **The interaction-QA matrix's `O` marks are dark-mode observations** for rows
  1-13. Light inherits the `C` marks and none of the `O` marks.
- **The rule and tint alphas are a design judgement**, not a measurement. The
  owner's eye ruled them right; no number did.
- **The review-stop facsimile was not the live page.** It used the real token
  values and type scale but fell back to Georgia, since the sandbox blocks
  external fonts. The binding verdict was always the live check, and was.
