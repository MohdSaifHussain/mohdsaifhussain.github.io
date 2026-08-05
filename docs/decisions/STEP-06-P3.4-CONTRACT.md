# STEP-06 (P3.4): CSP, security posture, and the accessibility passes

**Project:** mohdsaifhussain.github.io | **Phase:** P3.4, 4 of 5 | **Date:** 2026-08-06
**Status:** Specified, not started. Awaiting the director's approval, including rulings on Q1–Q3 (§7).
**Tier:** FULL

**Depends on:**
- **STEP-03 (P3.1), CLOSED** — the gate architecture; `INLINE_STYLE`/`INLINE_SCRIPT` enforced since the first template, so **this phase's CSP work is a no-op rather than a refactor**. That was the point of requirement 3.3 three phases ago.
- **STEP-04 (P3.2), CLOSED** — metadata, JSON-LD, `referrer no-referrer`, `rel="noopener noreferrer"`, zero third-party resources all already asserted as passing tests.
- **STEP-05 (P3.3), CLOSED** — the interaction-QA matrix, which the keyboard pass builds on rather than repeats.
- Charter C-06–C-09, C-11, C-18–C-22, and §7's platform constraint register.

**Standing rule:** every implementation follows the top applicable standard; each requirement names its governing standard. If a standard is ambiguous, stop and ask.

**Standing principle, adopted P3.2:** *local success is not evidence about CI; any figure destined for /audit is measured in the environment that publishes it.*

---

## 1. Objective

Apply the maximum security posture GitHub Pages permits, prove it by execution rather than by reading, and complete the accessibility passes that need a human and a screen reader.

**Exit criterion:** the deployed site loads with a strict CSP and **zero console violations, captured from a real browser run**; every contrast ratio is recomputed from the token values rather than quoted; and the keyboard and NVDA passes are complete with findings logged honestly.

## 2. Deliverables

| ID | Deliverable | Governing standard(s) |
|---|---|---|
| D1 | CSP via `<meta http-equiv>` — `default-src 'self'`, no `unsafe-inline`, no `eval`, explicit allowlist | **C-18**; CSP Level 3, fetched and cited |
| D2 | **O-10 discharged by execution** — the deployed pages loaded in a real browser, console messages captured, zero CSP violations, JSON-LD intact | **C-18**; doctrine rule 4 |
| D3 | Third-party and SRI audit — target state zero third-party resources; SRI documented as inapplicable where nothing external loads | **C-19** |
| D4 | Referrer policy and external-link audit, re-verified on rendered output | **C-20** |
| D5 | Cookie / localStorage / fingerprinting audit — expect zero of each | **C-21** |
| D6 | Counter posture recorded: `VISITS —`, zero third-party (decision D-03) | **C-22** |
| D7 | `tools/check_contrast.py` — every foreground/background pair **recomputed** from `tokens.css` by the WCAG formula, never quoted from the handoff table | **C-09**; WCAG 2.2 §1.4.3 / §1.4.6 |
| D8 | Full keyboard pass, every page, every interactive element | **C-07** |
| D9 | **NVDA smoke test** on Windows — director-owned; findings logged whatever they are | **C-08** |
| D10 | C-11 pass — `lang` correct, text to 200% without loss, no information by colour alone | **C-11** |
| D11 | axe-core: zero violations on every page | **C-06** |
| D12 | Test suite extended; contrast and CSP assertions added | Policy from P3.1 |

## 3. Requirements

- **3.1** The CSP contains **no `'unsafe-inline'` and no `'unsafe-eval'`**, for scripts or styles. The zero-inline discipline held since P3.1 makes this achievable without a refactor; if it turns out not to, that is a defect in the discipline and gets logged as one. *Standard: C-18.*
- **3.2** **O-10 closes on captured console output, not on my reading of a specification.** P3.2 verified JSON-LD's CSP safety against WHATWG HTML; that was correct and it was not execution. *Standard: doctrine rule 4.*
- **3.3** Contrast ratios are **computed from the hex values in `tokens.css`** by the WCAG relative-luminance formula. The handoff's stated ratios are treated as claims to be checked, not as inputs. *Standard: C-09; doctrine rule 13.*
- **3.4** Every contrast pair is reported with the **text size and weight it is actually used at**, because the AA threshold differs for large text. A ratio without its usage context is not a conformance statement. *Standard: WCAG 2.2 §1.4.3.*
- **3.5** The keyboard pass covers **every page**, not a sample, and records the tab order actually observed. *Standard: C-07.*
- **3.6** **NVDA findings are logged whatever they are.** A screen-reader pass that finds nothing is reported as what it examined and why it is confident, never as a bare pass. *Standard: C-08; doctrine.*
- **3.7** Where the platform makes a control impossible, it is declared in the constraint register and **never** claimed as met. *Standard: charter §7, §8.*
- **3.8** No cookie, no `localStorage`, no fingerprinting surface is introduced. *Standard: C-21.*
- **3.9** Close commands PowerShell 5.1-safe.

## 4. Out of scope

Lighthouse CI, the Nu validator, `audit.json` wiring and real published scores (P3.5) · SOP.md, release rehearsal, tag (P3.5) · light mode (v1.1) · the deferred owner-measured counts.

**Note on C-06:** axe belongs to this phase as a *condition to satisfy*; wiring it into CI so it **writes** `data/generated/audit.json` is P3.5. Q1 below decides where the tooling lands.

## 4a. Review stop

**Halt after D1–D7, before D8–D11.**

CSP and contrast are load-bearing and machine-checkable; the keyboard, NVDA and 200%-zoom passes are human work that assumes the machine-checkable layer is already correct. Running the manual passes first would mean repeating them after any CSP fix. At the stop I will:

1. Show the CSP as deployed, and the captured console output proving zero violations (O-10).
2. Show every contrast ratio **recomputed**, beside the handoff's stated value, and name any disagreement.
3. Show `check_contrast.py` refusing a deliberately failing pair.

## 5. Exit checklist

- [ ] CSP present on every page; **no `unsafe-inline`, no `unsafe-eval`**
- [ ] **O-10: zero CSP violations captured from a real browser run of the deployed site**
- [ ] JSON-LD still parses with the CSP active
- [ ] **Negative:** a deliberately inline script is refused by the CSP — demonstrated, not assumed
- [ ] `check_contrast.py` exits 0; every pair recomputed with its usage context
- [ ] **Negative:** a failing pair exits non-zero with its measured ratio
- [ ] Zero third-party resources; zero cookies; zero `localStorage`
- [ ] Keyboard pass complete, every page, tab order recorded
- [ ] **NVDA findings logged — including "none found", with what was examined**
- [ ] Text to 200% without loss of content or function
- [ ] axe: zero violations, every page
- [ ] Platform-impossible controls declared, not claimed

## 6. Obligations entering P3.4

| # | Obligation | Owner | State |
|---|---|---|---|
| **O-10** | **JSON-LD CSP behaviour confirmed by execution, not spec** | **P3.4 / D2** | **Open — this phase discharges it** |
| O-8 | `font-display: swap` measured against Lighthouse | P3.5 | Carried |

**Deferred, no owner:** owner-measured counts for the remaining three projects · light mode (v1.1) · per-repo `stats.json` live counts (v1.1) · a possible click-feedback animation, parked for owner decision now that P3.3's motion has shipped.

## 7. Numbered questions — for the director before building

**Q1 — Where does browser tooling land, and what may it be used for?** O-10, axe (C-06) and the CSP console check all need a real browser. I have none. P3.5 needs one anyway for Lighthouse.

- **(a) Bring headless-browser tooling forward into this phase, in CI (recommended).** Add Playwright to the CI job to load each deployed page, capture console output, and run axe. O-10 then closes on evidence produced **in the environment that publishes the site**, which is exactly your standing principle. P3.5 then only adds Lighthouse, the validator, and the `audit.json` wiring. Cost: one more CI dependency, arriving a phase earlier than planned.
- (b) Defer all browser verification to P3.5; this phase builds the CSP by construction and you check the console by eye. Honest, but O-10 would close on observation rather than captured output, and axe would slip a phase.
- (c) Install browser tooling locally for me as well. I would advise against it: a figure I measure locally is precisely what your standing principle says is not evidence about the published site.

**Q2 — What is the evidence standard for the NVDA pass (C-08)?** Only you can run it — it is Windows and a screen reader, and there is no substitute.

- **(a) Written findings against a stated checklist (recommended).** You work a per-page list — landmarks announced, headings navigable, links meaningful out of context, marks not read as noise, tables sensible — and record the result per item, including "nothing found" with what was examined. Cheap, repeatable at every release, and it satisfies 3.6's requirement that a clean pass says what it looked at.
- (b) A recorded transcript of the session, archived in the repo. Stronger evidence, larger artefact, and it would need reviewing for anything C-33 prohibits before it could be committed.
- (c) A bare pass/fail. I would not recommend it — it is the shape of evidence that cannot be checked later.

**Q3 — How should the contrast result be claimed?** C-09 requires ≥ 4.5:1 for body text and adopts ≥ 7:1 "as target, not claim". The `dim` token is stated at 5.1:1 and is used for metadata and small-caps labels — above AA, below the AAA target.

- **(a) Report per-token measured ratios with usage context, claim AA met in full, and state plainly which tokens reach the 7:1 target and which do not (recommended).** That is the exact width of the evidence, and it matches how the charter itself worded the AAA aim.
- (b) Claim AAA and restrict `dim` to uses where the large-text threshold applies. Achievable but it would change the design at this stage.
- (c) Report only AA and omit the 7:1 discussion — which would quietly drop a target the charter set for itself.

## 8. Honest limits entering this phase

- I have no browser. Under Q1(a) the console and axe evidence is produced **by CI**, not by me; I write the job and read its output. Under Q1(b) that evidence is yours.
- `frame-ancestors` and `report-uri` are **not settable via `<meta>`** — I will confirm this against the CSP specification in-phase rather than assert it from memory, and whatever it says gets declared in the constraint register, since it bears on the existing A4.1 declaration about X-Frame-Options.
- The NVDA pass cannot be performed or verified by me in any form. Its evidence is entirely yours.
- axe and Lighthouse disagree with each other and with manual review on some criteria; zero axe violations is **not** the same as "accessible", and /audit will say so rather than let the number stand alone.
