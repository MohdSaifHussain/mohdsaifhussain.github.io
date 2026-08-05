# Accessibility passes — C-07, C-08, C-11

Machine checks live elsewhere: axe-core and CSP violations are measured per
deploy by `tools/browser_audit.py` in CI, contrast by `tools/check_contrast.py`.

**axe found nothing, and that is not the same as accessible.** Automated tooling
catches a minority of real barriers. The passes recorded here are the part no
tool substitutes for, which is why C-08's evidence is entirely the owner's.

**Whose evidence this is.** Every finding below was observed by the owner on
Windows with NVDA, in a real browser. The builder has no browser and no screen
reader, and did not perform, witness, or infer any of it.

---

## The checklist of record (C-08)

Director-supplied, 2026-08-06. Recorded as **the** checklist rather than a
builder-drafted one, and reused unchanged at every future release so results
stay comparable.

1. Page title and heading walk
2. Meaningful link names
3. Marks silent
4. Nav announces current page
5. Clock does not re-announce over a one-minute listen

Point 5 exists because the truth-strip clock updates every second. A live region
that re-announced on each tick would make the page unusable with a screen
reader, and it is the kind of defect that is invisible to sighted testing and to
axe alike.

---

## C-11 — 200% zoom, all five pages

**Observed by the owner, 2026-08-06:** no content lost, no overlap, no
horizontal scroll. Confirmed complete as written. **C-11 MET.**

## C-07 — keyboard pass, all five pages

**Observed by the owner, 2026-08-06:** skip link worked on first Tab; every link
reachable; focus visible throughout; tab order logical; slider scrolled with
arrow keys; no traps. Confirmed complete as written, no deviations. **C-07 MET.**

Cross-reference: the slider carries the only `tabindex` on the site, because it
genuinely is a scroll region (C-14). Every other component was deliberately left
unfocusable to avoid dead tab stops — see the A3.4 ruling and STEP-05 Q2.

## C-08 — NVDA, per page

**C-08 status: MET IN PART, declared under charter §8.** Director's ruling,
2026-08-06: *"NVDA covered Home only. Close C-08 as a declared partial — Home
verified, the other four pages named on /audit as unverified by screen reader."*

| Page | 1. Title & headings | 2. Link names | 3. Marks silent | 4. Current page | 5. Clock quiet |
|---|---|---|---|---|---|
| **Home** | announced; headings walked sensibly | — | marks silent | current page announced | **silent over one minute** |
| Projects | **not verified by screen reader** | — | — | — | n/a |
| Experience | **not verified by screen reader** | — | — | — | n/a |
| Certifications | **not verified by screen reader** | — | — | — | n/a |
| Audit | **not verified by screen reader** | — | — | — | n/a |

**What the partial does and does not cover.** The pass exercised the five
checklist points on Home. The other four pages were **not** examined with a
screen reader, and nothing here should be read as evidence about them. They
share the same nav, footer, mark macros and heading structure, so there is a
reasonable expectation they behave alike — **an expectation is not an
observation**, and this row is the difference between the two.

Declared on /audit as A4.9 rather than left implicit, so a reader of the site
learns the limit from the site itself rather than from this file.

**Carried forward:** the remaining four pages are re-offered at every release
under the same five-point checklist. The limit narrows only when a page is
actually examined — never by the passage of time or by the site being unchanged.

**Home's result confirms the design intent behind two rulings:** the marks are
`aria-hidden` with adjacent text carrying meaning (the D-14 ruling), and the
clock is a plain text node with no live region (D6) — so neither becomes noise.

---

## Honest limits

1. The builder cannot verify, reproduce or sanity-check any finding here. They
   are recorded as the owner's observations and attributed as such.
2. A clean pass records **what was examined**, never a bare "pass" — which is
   why the checklist above is part of the record rather than a working note.
3. NVDA is one screen reader on one platform. C-08 asks for an NVDA smoke test
   specifically; it is not a claim about JAWS, VoiceOver, Orca or TalkBack, and
   /audit will not imply otherwise.
