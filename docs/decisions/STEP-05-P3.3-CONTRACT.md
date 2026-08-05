# STEP-05 (P3.3): The three animations, reduced motion, clock, interaction QA

**Project:** mohdsaifhussain.github.io | **Phase:** P3.3, 3 of 5 | **Date:** 2026-08-06
**Status:** Specified, not started. Awaiting the director's approval, including rulings on Q1–Q3 (§7), which gate deliverable D4.
**Tier:** FULL

**Depends on:**
- **STEP-03 (P3.1), CLOSED** — the gate architecture, `tokens.css` as sole source, `_mark()`, `--motion-reveal` already tokenised with a `prefers-reduced-motion` override in place awaiting its consumer.
- **STEP-04 (P3.2), CLOSED** — all five pages rendered from data; the scroll-snap slider built as layout under reading R-06, with its C-14/C-15 verification **explicitly deferred to this phase**; the responsive derivation approved as owner-reviewed new design (O-6).
- STEP-02-HANDOFF **§5 — the complete animation list, closed at three** — and §4 (the evidence-layer component spec), §6 (the frozen interaction-QA rule).
- Charter C-10, C-12–C-16.

**Numbering:** `STEP-NN` for these files, `P3.x` for phases, charter "Phase 3" for the whole build.

**Standing rule:** every implementation follows the top applicable standard; each requirement names its governing standard. If a standard is ambiguous, stop and ask.

---

## 1. Objective

Ship the three specified animations and nothing else, prove the reduced-motion kill switch leaves the site complete and coherent, and put every component through the frozen interaction-QA rule in every state.

**Exit criterion:** `check_animations.py` proves exactly three animations ship and that motion touches only `transform`/`opacity`; the site is fully usable and complete with motion disabled; and no overlay or hover layer covers any interactive element in any state, demonstrated state by state.

## 2. Deliverables

| ID | Deliverable | Governing standard(s) |
|---|---|---|
| D1 | **A3.1 Home evidence reveal** — opacity only, 200ms, `pointer-events:none`, layer spanning the name+problem columns ONLY (`left:148px; right:248px`), driven by row-level JS state, external script | Handoff §4, §5; C-12, C-15; **handoff §6 interaction-QA rule** |
| D2 | **A3.2 verification** — the slider built in P3.2 verified against C-14 and C-15 and recorded in the audit list. Native scroll only; position visible; keyboard and swipe operable | C-14; reading R-06 (director-endorsed) |
| D3 | **A3.3 hover state** — instant colour swap, no transition, on links and nav | C-16; handoff §5 |
| D4 | **Receipts row hover/focus state on Experience** — background tint plus text stepping from the `body` token to the `bright` token, **instant** (A3.3 family, not a new timed animation), `:hover` and `:focus` receiving **identical** treatment for keyboard parity, and **no layout shift**. **Explicitly NOT text magnification** — rejected by the director for motion-sensitivity, blur, and touch-user reasons | Director's proposal; C-10, C-12, C-16; **§7 questions Q1–Q2 must be ruled first** |
| D5 | **Reduced-motion kill switch** — `--motion-reveal: 0ms` already lands in `tokens.css`; prove every state stays reachable and the site stays complete and coherent with motion off | **C-10** (AAA 2.3.3 adopted as a hard rule) |
| D6 | **Truth-strip IST clock** — `Intl`, `Asia/Kolkata`, 1s tick, external script, with a server-rendered no-JS fallback | Handoff §3; C-18 (external script only) |
| D7 | `tools/check_animations.py` — asserts exactly three shipped animations; motion properties limited to `transform`/`opacity`; durations within C-15 bounds | **C-12, C-15**; doctrine rule 5 |
| D8 | **Interaction-QA matrix** — every component × every state (rest / hover / focus-visible / active / keyboard / reduced-motion / touch), written up with a pass mark per cell | **Handoff §6, the frozen project rule** |
| D9 | Test suite extended, one test per new gate behaviour, **including the basis-agreement guard of §6** | Policy from P3.1; doctrine rule 8 |

## 3. Requirements

- **3.1** **The shipped-animation list stays closed at three.** Any motion not on handoff §5's list is a defect, not a feature. `check_animations.py` fails if a fourth appears. *Standard: C-12; handoff §5.*
- **3.2** Motion animates `transform` and `opacity` only. No `width`/`height`/`top`/`left`. Micro-interactions 150–250 ms; transitions ≤ 400 ms. *Standard: C-15.*
- **3.3** The A3.1 evidence layer is `pointer-events:none` and spans the name+problem columns only. **The links column is never covered in any state.** This is the defect the committed design was rebuilt to fix; it is re-proved here, not assumed. *Standard: handoff §4, §6.*
- **3.4** Every interactive element gives feedback within 100 ms of input. *Standard: C-16.*
- **3.5** With `prefers-reduced-motion: reduce`, every state remains reachable and the site remains complete and coherent — not merely still. *Standard: C-10.*
- **3.6** All scripts are external files. No inline script bodies; `application/ld+json` data blocks remain the sole exception, on the HTML-standard authority cited in `build.py`. *Standard: C-18.*
- **3.7** The clock degrades honestly without JS: the server-rendered fallback shows the snapshot's "as of" stamp, never an empty slot or a frozen fake time. *Standard: C-27.*
- **3.8** No new tab stop is created on non-interactive content. *Standard: C-07; WAI-ARIA 1.2 authoring practices — see Q2.*
- **3.9** D4 introduces **no layout shift** in any state. *Standard: C-02 (CLS = 0.00).*
- **3.10** Close commands PowerShell 5.1-safe.

## 4. Out of scope

CSP meta and the zero-inline audit (P3.4) · keyboard/NVDA/contrast passes as *conditions* (P3.4 — this phase produces the interaction-QA matrix, which P3.4 builds on) · Lighthouse/axe/validator wiring and real audit scores (P3.5) · SOP.md, release, tag (P3.5) · light mode (v1.1, R-11).

## 4a. Review stop

**Halt after D1–D5 and D7, before D6 and D8.**

The animation contract and its gate are load-bearing: the clock and the QA matrix are surface layers that assume the motion rules already hold. A defect in the evidence layer found after the QA matrix is written means the matrix documented the wrong thing. At the stop I will:

1. Quote the exact lines proving the A3.1 layer is `pointer-events:none` and bounded to two columns, and demonstrate the links column reachable in every state.
2. Show `check_animations.py` refusing an injected fourth animation, and accepting the real three.
3. Show the site under reduced motion with every state still reachable.
4. Report A3.2's C-14/C-15 verification, carried in from P3.2's R-06.

## 5. Exit checklist

- [ ] `check_animations.py` exits 0; exactly three animations ship
- [ ] **Negative:** an injected fourth animation, and a `width` transition, each exit non-zero with distinct reason codes
- [ ] **Positive:** the real three do not trip it
- [ ] A3.1 layer proven `pointer-events:none`, bounded to two columns; **links clickable in every state, demonstrated**
- [ ] Reduced motion: every state reachable, site complete and coherent — director toggles and reads
- [ ] Clock ticks; **with JS disabled the fallback shows the snapshot stamp**, not a blank or a frozen time
- [ ] D4 hover/focus: identical treatment, no layout shift, no new tab stop on non-interactive content
- [ ] Interaction-QA matrix complete, every component × every state
- [ ] Build still deterministic; C-33 and content checkers still clean

## 6. Deferred: owner-measured counts for the remaining three projects

**Superseding the director's earlier message:** re-measurement of the delivery-engine, analystkit and opskit suites is **DEFERRED, not incoming.** No obligation is open, and nothing in this phase waits on it.

The resume-baseline figures **stand as shipped**. They are true as stated, each carries its version anchor and evidence link, and `_metrics_basis` describes their basis accurately. Nothing here is pending or provisional; it is simply sourced differently from the TS-Sentry entry, and says so.

**Recorded in the deferred list:** the owner may supply owner-measured counts later as a signed data edit, upgrading that entry's basis at that time. Per-entry, not all at once — the TS-Sentry entry already demonstrates the two bases coexisting.

**One guard ships now, because the deferral is exactly what makes it necessary** (doctrine rule 8). `_metrics_basis` and the entries must agree about which bases are in use:

- if any entry is resume-baseline, the resume-baseline sentence must be present;
- once **no** entry is resume-baseline, that sentence must be gone.

A test asserts both directions. Today it passes on the first. The day the last entry is upgraded and the sentence is left behind, it fails — so the sentence cannot quietly outlive its own truth while nobody is looking at it. This guards a change that may be months away, which is the only time such a guard is worth writing.

## 7. Numbered questions — for the director before building D4

The receipts row state is a good idea and I am not arguing against it. Two things about it are genuinely ambiguous, and both change what gets built.

**Q1 — Which question does it answer (C-12)?** C-12 requires every animation to answer *exactly one* of *where am I* / *what just happened* / *what can I do*, and to be listed on /audit with that declared purpose.

You assigned it to the A3.3 family, whose declared answer is **WHAT CAN I DO**. But the Experience receipts rows are not interactive — they contain no link, button or control. A hover state that declares "what can I do" on a row where nothing can be done advertises an affordance that does not exist, which is the kind of small dishonesty C-12 exists to catch.

- **(a) Declare it WHERE AM I (recommended).** It is a reading-position aid: it tells you which row you are on in a dense table. That is truthful, and it is the same question A3.2 answers. A3.3's audit row widens to name row states alongside links and nav, and the count stays three.
- (b) Keep it WHAT CAN I DO, and make the rows genuinely actionable — but there is nothing for them to link to, so this means inventing a destination.
- (c) Keep it WHAT CAN I DO as declared, accepting that the row offers no action.

**Q2 — How is keyboard parity achieved without a dead tab stop (C-07)?** You asked for `:hover` and `:focus` to receive identical treatment. A non-interactive `<article>` cannot receive focus unless given `tabindex="0"`, and WAI-ARIA authoring practice advises against focusable non-interactive elements: it adds tab stops that lead nowhere, lengthening the keyboard path and giving screen-reader users a stop with no action (C-07, C-08).

- **(a) `:focus-within`, plus hover (recommended).** The row highlights when anything inside it takes focus. Genuine parity **the moment a row contains a focusable element**, and it adds zero tab stops. Honest limit: with today's data no receipts row contains a focusable element, so the focus half is inert until one does — and I would declare that on /audit rather than let it read as working.
- (b) `tabindex="0"` on each of the six role rows. True parity today, at the cost of six tab stops that perform no action. Would need declaring against C-07.
- (c) Hover only, with the absence of a keyboard equivalent declared openly on /audit, on the grounds that non-interactive content needs no focus state.

**Q3 — Does A3.3's audit row widen, or does this become A3.4?** Handoff §5 calls its list complete. My reading of your ruling is that this joins A3.3 rather than extending the list, so the count stays three and `check_animations.py` keeps asserting three. I want that confirmed rather than assumed, because the alternative silently breaks "nothing else ships".

## 8. Obligations entering P3.3

| # | Obligation | Owner | State |
|---|---|---|---|
| O-8 | `font-display: swap` measured against Lighthouse | P3.5 | Carried |
| O-10 | JSON-LD CSP behaviour confirmed by execution, not spec | **P3.4** | Carried |

**Deferred, not an obligation** (director, 2026-08-06): owner-measured counts for delivery-engine, analystkit and opskit. No phase owns this and nothing waits on it; the shipped figures are accurate as stated. It becomes a signed data edit whenever the owner chooses, guarded by §6's basis-agreement test.

**Deferred list, carried forward:** light mode → v1.1 (R-11, A4.8) · genuinely live test counts via per-repo `stats.json` → v1.1 (DECISIONS 3.1.3a) · a possible click-feedback animation → parked for owner decision **after** P3.3's motion ships; nothing changes in the shipped-animation list now.

**Discharged before this phase:** O-1, O-2 (closed by decision), O-3, O-6, O-9, O-11.

## 9. Honest limits entering this phase

- I have no browser in this environment. Motion smoothness, the 60fps requirement in C-15, and "feedback within 100 ms" (C-16) are **not directly measurable by me**; I can prove the properties and durations in code, and the director observes the behaviour. Stated plainly rather than implied.
- A3.2 was built as layout in P3.2 under R-06; its C-14/C-15 verification is carried into this phase and is a *verification*, not a rebuild.
- The interaction-QA matrix is a manual artefact. Where a cell depends on observation, it records who observed it.
