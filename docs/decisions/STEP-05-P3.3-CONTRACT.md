# STEP-05 (P3.3): The three animations, reduced motion, clock, interaction QA

**Project:** mohdsaifhussain.github.io | **Phase:** P3.3, 3 of 5 | **Date:** 2026-08-06
**Status:** **CLOSED 2026-08-06.** D1–D9 shipped and deployed. Phase-close ritual §11 executed by hand by the director, all steps matching pre-stated expectations: exit 0 throughout, hash `c6d32ad5345d78f3` restored after the poison step, 41 passed / 1 skipped with its reason printed, `--verify-links` 12 URLs at 200. **The two-direction gate proof was performed:** renaming A3.4 to A3.7 in the spec made the gate FAIL as required, proving declared-but-unshipped motion is refused; restored and re-verified. By-eye: with JS disabled Home reads `SNAPSHOT hh:mm IST` with no dot; re-enabled, the dot appears and the clock crossed a minute boundary with seconds advancing and nothing else moving — D-31 reservation holds. D-31, D-32, D-33 dispositions endorsed; D-33 supersession-not-edit handling noted as correct record practice.
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

> **Corrected 2026-08-06.** This said *"exactly three animations ship"*. It is now **four**, and the criterion is not a count at all: `check_animations.py` proves that **what ships matches what `data/audit-spec.json` declares, in both directions**. Changed by the Q3 ruling (§7), which added A3.4. Found by re-reading the contract against its own rulings during the adversarial pass — §1, §3.1 and §5 had been left stating the pre-ruling number, so the document contradicted itself and a reader of §1 alone would have taken the wrong rule.

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
  > **Corrected 2026-08-06.** The list is **four**, and the rule is no longer a count: *"nothing else ships"* is preserved as **the list changes only by recorded ruling, never silently.** Any **undeclared** motion is a defect; a declared one that does not ship is also a defect. Changed by the Q3 ruling (§7). A frozen count could only have been honoured by refusing a genuine improvement or by breaking quietly.
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
      *(corrected: **four**; the check is list-agreement in both directions, not a count — Q3 ruling)*
- [ ] **Negative:** an injected fourth animation, and a `width` transition, each exit non-zero with distinct reason codes
      *(corrected: an **undeclared** animation, and separately a **declared-but-unshipped** one)*
- [ ] **Positive:** the real three do not trip it *(corrected: the real four)*
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

## 7. Numbered questions — RULED 2026-08-06, contract APPROVED

**Q1 — RULED: WHERE AM I.** The director accepted the correction and named the imprecision in their own first ruling: they had classified by *mechanism* (instant state), but **C-12 classifies by declared answer**, and WHAT CAN I DO on a control-free row would advertise a false affordance. The receipts state is a reading-position aid.

**Q2 — RULED: `:focus-within` plus `:hover`, no `tabindex` on non-interactive rows.** Dead tab stops are the worse trade against C-07 and C-08. The honest limit — *the focus half is inert until a receipts row contains a focusable element* — is declared on /audit as stated, not left to read as working.

**Q3 — RULED: it becomes A3.4, its own entry.** A consequence of Q1: an animation answering a different question is a different animation. The shipped list **updates to four**; `check_animations.py` asserts the **declared** list rather than a hardcoded three; recorded as an owner-directed addition to handoff §5 with this rationale.

> **"Nothing else ships" is preserved as: the list changes only by recorded ruling, never silently.**

That sentence is the actual guarantee, and it is stronger than a frozen number. A frozen count can only be honoured by refusing good changes or by breaking it quietly; a list that moves only under a recorded ruling can absorb a genuine improvement while still making an undeclared animation a defect. `check_animations.py` therefore compares what ships against `data/audit-spec.json`'s declared list — so adding an animation without declaring it fails the build, and declaring one without shipping it fails too.

## 7a. Original numbered questions, as put

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

## 10. Outcome

**Status:** Built and deployed. Awaiting the director's phase-close verification (§11).

**Shipped:** D1–D9. 41 tests passing, 1 skipped with a printed reason. Four checkers: 12 build gates, 16 C-33 controls, 10 content controls, 9 animation controls.

### Exit checklist, evidenced

- [x] `check_animations.py` exits 0 — *4 declared, 4 implemented, both directions agree.*
- [x] Negative controls — *undeclared A3.9, `@keyframes`, `width` transition, `transition: all`, a **timed** colour transition, and a 900ms duration all refuse with distinct codes.*
- [x] Positive control — *real `opacity 200ms` and `transform 250ms` accept; real CSS clean.*
- [x] A3.1 bounded and inert — *`left: calc(120px + …)`, `right: calc(220px + …)` derived from grid tokens, plus `pointer-events: none`. Either alone suffices. **Links clickable with the layer open, observed by the director 2026-08-06.***
- [x] Reduced motion — *one lever, `--motion-reveal: 0ms`. Director observed the reveal still functioning with zero transition.*
- [x] Clock degrades honestly — *no-JS renders `SNAPSHOT 02:45 IST`; the live dot appears only once ticking; without `Intl` the snapshot label stays rather than substituting non-IST local time.*
- [x] D4 identical `:hover`/`:focus-within`, no `tabindex`, **no layout shift** — *background and colour only; verified by inspection of the only two rules involved.*
- [x] Interaction-QA matrix complete — *13 components × 7 states, with C/O/? distinguished.*
- [x] Deterministic build; C-33, content and animation checkers clean.

### Defects found by running it, or by reading it against its claims

1. **D-29** — the weekly Action approved in P3.2 **was never built**; an approved control existed only on paper for a phase. Found by reading the prior rulings back against the repo.
2. **D-31** — the clock's honest fallback **shifted the page**: an 18→12 character swap after DOMContentLoaded, inside the CLS window, against C-02. I built the correct behaviour and then let it break a different condition.
3. **D-32** — a test that **passed by asserting nothing** once the data it guarded changed. Same class as D-18: green for the wrong reason. Now cannot go vacuous, and skips print their reasons.
4. **D-30** — a reported defect that four measurements did not reproduce; the edit was refused and the report withdrawn on the evidence.

### Readings and deviations, recorded

- **A3.4 added to the handoff §5 list by recorded ruling.** The list is four. *"Nothing else ships"* is preserved as **the list changes only by recorded ruling, never silently** — and `check_animations.py` enforces that in both directions, which a frozen count could not.
- **Q1 correction accepted from the builder:** the director had classified A3.4 by mechanism; C-12 classifies by declared answer. Declared **WHERE AM I**, not WHAT CAN I DO, because the rows carry no control.
- **Mobile inline metrics** — approved as an owner-reviewed design ruling: nothing may be reachable by hover alone.

### Obligations

**Discharged:** the property/observation split (director's observations recorded in the QA matrix with dates).
**Carried to P3.4:** O-10 (JSON-LD CSP behaviour confirmed by execution).
**Carried to P3.5:** O-8 (`font-display: swap` measured).
**Deferred, no owner:** owner-measured counts for the remaining three projects, guarded by the basis-agreement test.

### Honest limits

1. **`check_animations.py` identifies implementations by marker comment.** It proves the declared list and the CSS agree *by name*, not that the CSS behaves as its name claims. Three of the four carry the director's observation; that is what closes the gap.
2. I have no browser. 60fps (C-15) and 100ms feedback (C-16) are **not measurable by me** and are marked `O` in the QA matrix or left `?`.
3. **A3.4's focus half is inert** — no receipts row contains a focusable element, so `:focus-within` cannot fire on today's content. Declared on /audit.
4. The A3.1 layer is hidden below 900px; all metrics render inline there instead, so nothing is hover-only.

## 11. Phase close — the director's ritual

```powershell
# 1. Build, tests, all four checkers. Expect exit 0 throughout,
#    "41 passed, 1 skipped", and the skip REASON printed.
python build.py;                          "exit=$LASTEXITCODE"
python -m pytest;                         "exit=$LASTEXITCODE"
python tools\check_animations.py --selftest; "exit=$LASTEXITCODE"
python tools\check_c33.py;                "exit=$LASTEXITCODE"
python tools\check_content.py;            "exit=$LASTEXITCODE"

# 2. NEGATIVE PATH — declare an animation that does not ship.
#    Expect exit 1, REASON=UNSHIPPED_ANIMATION.
Copy-Item data\audit-spec.json data\audit-spec.json.bak
(Get-Content data\audit-spec.json -Raw) -replace '"id": "A3.4"','"id": "A3.7"' | Set-Content data\audit-spec.json -Encoding utf8
python tools\check_animations.py;         "exit=$LASTEXITCODE  (expect 1)"
Move-Item -Force data\audit-spec.json.bak data\audit-spec.json
python tools\check_animations.py;         "exit=$LASTEXITCODE  (expect 0)"

# 3. Evidence links resolve (the networked check, run by hand here).
python tools\fetch_stats.py --verify-links; "exit=$LASTEXITCODE"

# 4. By eye, on the live site.
start https://mohdsaifhussain.github.io/
```

| Scenario | Expected | Observed |
|---|---|---|
| `python build.py` | exit 0, hash `c6d32ad5345d78f3` | |
| `python -m pytest` | exit 0, 41 passed **1 skipped, reason printed** | |
| `check_animations.py --selftest` | exit 0, 9 controls PASS | |
| **A3.4 renamed to A3.7 in the spec** | **exit 1, `REASON=UNSHIPPED_ANIMATION`** | |
| Restored | exit 0 | |
| `--verify-links` | exit 0, 12 URLs at 200 | |
| **Clock across a minute boundary** | **seconds tick; nothing beside it moves** | |
| **JS disabled, reload Home** | **reads `SNAPSHOT hh:mm IST`, no dot** | |

**The row worth keeping in view** is the renamed-animation one. It is the only step that demonstrates the *second* direction of the gate — that declaring motion which does not ship fails too. The first direction was already proved by the selftest; this one proves the list cannot drift away from reality in either direction.

**Read by eye:** with JS off the clock reads `SNAPSHOT` and carries no dot; with JS on the dot appears and seconds advance without the strip shifting. Tab into a Home ledger row — the evidence should reveal and REPO should still be clickable. Hover an Experience receipts row — the tint should appear with no text reflow.


