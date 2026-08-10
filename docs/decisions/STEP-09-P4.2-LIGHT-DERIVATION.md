# P4.2 — how the light palette was derived

**Filed:** 2026-08-10, on the owner's condition that the derivation publish its
work, so a one-time act is inspectable rather than taken on trust.

**Authority:** charter §5 — *"Palette: monochrome (near-black / off-white) plus
exactly one accent color. Dark-first; light mode optional later, never at the
cost of C-09."* Closing R-11 and limitation A4.8.

**The division of labour this file exists to make honest.** Deriving the palette
was a judgement call made once, by the method below. **Verifying it is
permanent**: `tools/check_contrast.py` recomputes every ratio in both themes on
every build and refuses if any constraint breaks. Committed hex literals are
only honest when something checks them forever after; this file says where they
came from, and the checker says whether they still hold.

---

## The constraints

Set by the owner, and stricter than C-09 alone:

1. **AA in full**, for every pair at the size it is actually used.
2. **≥7:1 wherever the dark theme achieves it.** Light mode may not cost a
   target the site already meets.
3. **`--dim` may not worsen** relative to its dark-mode 5.78:1. It is the one
   token below 7:1, and its shortfall may not deepen.

Each has its own reason code in the checker: `CONTRAST_BELOW_AA`,
`SEVEN_TO_ONE_LOST`, `DIM_WORSENED`.

## The derivation rule

- **`--light-bg` is chosen**, not solved: `#faf9f6`, the warm off-white charter
  §5 names. It is the one free parameter, and everything else is solved against
  it.
- **`--light-ink` is the dark palette's own background**, `#0d0d0c`, inverted.
  The light theme introduces no colour the site did not already contain.
- **`--light-body`, `--light-bright`, `--light-dim`**: keep the dark token's hue
  and saturation; solve its *value* until the measured ratio against
  `--light-bg` equals the dark token's measured ratio against `--dark-bg`. The
  legibility hierarchy is therefore mirrored, not re-invented — `--bright`
  carries more contrast than `--body` in both themes, which in light means
  darker.
- **`--light-accent`**: keep the amber's hue and saturation; solve to the **7:1
  floor**. Owner's ruling.
- **Rules and tints** (`--rule-mid`, `--rule-faint`, `--row-tint`) are the ink at
  low alpha. They are re-stated on the light ink's channels; the alphas were
  nudged (0.4 → 0.34, 0.25 → 0.20) because dark ink on a light ground reads
  heavier than light ink on a dark ground at the same alpha. These are
  non-text surfaces and carry no C-09 obligation, so they are a design
  judgement, stated as one rather than dressed as a measurement.

## The solved values

Every ratio below was recomputed by `check_contrast.py` from the committed
hexes, not transcribed from the solver.

| Token | Constraint applied | Dark hex | Dark measured | **Light hex** | **Light measured** |
|---|---|---|---|---|---|
| `--bg` | chosen (the free parameter) | `#0d0d0c` | — | **`#faf9f6`** | — |
| `--ink` | the dark `--bg`, inverted | `#f2f0eb` | 17.07:1 | **`#0d0d0c`** | **18.47:1** |
| `--body` | mirror the dark ratio | `#cfccc3` | 12.11:1 | **`#333230`** | **12.16:1** |
| `--bright` | mirror the dark ratio | `#e8e5dd` | 15.45:1 | **`#21201f`** | **15.45:1** |
| `--dim` | mirror; may not worsen | `#8f8c83` | 5.78:1 | **`#64625c`** | **5.79:1** |
| `--accent` | 7:1 floor (owner's ruling) | `#e8b64c` | 10.40:1 | **`#695222`** | **7.05:1** |

The inverted pair — `--bg` on `--accent`, used by the skip link and the PDF
button hover — measures 10.40:1 in dark and 7.05:1 in light. Both clear 7:1.

## Why the accent is bronze, and not amber

This is the visible cost of light mode, and it is not a matter of taste.

The brand amber `#e8b64c` has a relative luminance of 0.511. Against an
off-white ground, the maximum luminance a foreground may have is **0.093** to
reach 7:1 — and **0.183** even to reach AA alone. The amber exceeds the AA
ceiling by nearly 3×.

There is no amber that survives a light background at any WCAG-meaningful ratio.
The options were a legible bronze or a declared shortfall, and the owner ruled
for legibility. Dark mode keeps `#e8b64c` untouched.

One tempting escape was tested and refused: *dimming* the light background does
not help. For dark text on a light ground the ratio is
`(L_bg + 0.05) / (L_fg + 0.05)`, so lowering the background luminance lowers the
ratio — a "dim light" theme would need an even darker accent, not a lighter one.
Recorded because it is the wrong intuition, and a later reader will have it too.

## Reading R-16 — "exactly one accent color"

Charter §5 fixes *exactly one accent color*. The light theme gives that accent a
different hex. Read as: **one accent ROLE, themed** — the site has one accent,
not two, and it takes the value each theme can legibly carry. The alternative
reading, that the hex itself is frozen, would make light mode impossible under
C-09, which the same sentence explicitly permits. Recorded rather than assumed.

## What is NOT claimed here

- The rule/tint alphas are a design judgement, not a measurement. Said so above.
- These figures describe the palette, not the rendered page. Whether the light
  theme is *legible in practice* — marks, colophon, rules on real content — is
  the owner's eye check on the live site, in both themes, and is not
  substitutable by any ratio in this file.
