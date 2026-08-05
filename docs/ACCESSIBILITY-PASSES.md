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
horizontal scroll.

> ⚠ **Awaiting confirmation.** The submitted text read
> `[no content lost, no overlap, no horizontal scroll / anything seen]`. The
> portion before the slash is recorded above as the finding; the trailing
> `/ anything seen` is read as an unfilled template alternative. **Confirm, or
> supply what was seen.**

## C-07 — keyboard pass, all five pages

**Observed by the owner, 2026-08-06:** skip link worked on first Tab; every link
reachable; focus visible throughout; tab order logical; slider scrolled with
arrow keys; no traps.

> ⚠ **Awaiting confirmation.** The submitted text ended `no traps / deviations`.
> Recorded as "no traps"; the trailing `/ deviations` is read as an unfilled
> template alternative. **Confirm, or supply the deviations.**

Cross-reference: the slider carries the only `tabindex` on the site, because it
genuinely is a scroll region (C-14). Every other component was deliberately left
unfocusable to avoid dead tab stops — see the A3.4 ruling and STEP-05 Q2.

## C-08 — NVDA, per page

| Page | 1. Title & headings | 2. Link names | 3. Marks silent | 4. Current page | 5. Clock quiet |
|---|---|---|---|---|---|
| **Home** | announced; headings walked sensibly | — | marks silent | current page announced | **silent over one minute** |
| Projects | *not yet recorded* | | | | |
| Experience | *not yet recorded* | | | | |
| Certifications | *not yet recorded* | | | | |
| Audit | *not yet recorded* | | | | |

> ⚠ **C-08 IS NOT YET SATISFIED.** Four of the five pages have no recorded
> findings — the submitted text carried the literal placeholder `[findings]` for
> Projects, Experience, Certifications and Audit.
>
> These rows are left visibly empty rather than filled by inference. A screen
> reader pass is exactly the evidence that cannot be reconstructed from anything
> else in this repo, and a plausible-looking row would be indistinguishable from
> a real one to every future reader — including the owner.
>
> **C-08 reports UNMET until they are supplied.**

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
