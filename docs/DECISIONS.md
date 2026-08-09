# Technology and Approach Decisions

A living record of what this project chose, what it did not choose, and why.

**Every entry cites where the decision was actually made** (commit SHA, phase
file, or design-authority section). Entries harvested from an existing record
say so. Entries where no rationale was ever written down say *that*, and the
tradeoff is then given as a clearly marked retrospective rather than as invented
history. A decision log that manufactures reasons after the fact is worse than no
decision log, because it reads as evidence.

Each phase appends its decisions here.

Governing documents: `decisions/STEP-01-CHARTER.md` (frozen v1.0 + Amendment
Log) wins every conflict; `decisions/STEP-02-HANDOFF.md` wins every visual
question; `reference/design.html` is visual reference only and is never shipped
code.

---

## Phase P3.1: Scaffold, build pipeline, fonts, tokens, repo connection

| # | Decision | Alternative(s) not taken | Reason | Recorded in |
|---|---|---|---|---|
| 3.1.1 | **Tier FULL** for the whole build | (a) STANDARD; (b) FULL without a DECISIONS log | The build ends in a public deploy, a `v1.0.0` tag, and an /audit page making WCAG/CSP/Lighthouse claims to strangers. Charter §8 already mandates phased close, honest defect logging and numbered amendments. FULL adds this log and a rehearsed release | Director's ruling, session 2026-08-06 |
| 3.1.2 | **Global git identity set to `263689115+MohdSaifHussain@users.noreply.github.com`** before the first commit | (a) repo-local only; (b) keep the prior address and declare C-33 UNMET | Defect D-01: commit authorship is immutable once pushed, and the prior address would be permanently public. Director chose global scope deliberately, accepting the effect on other repos on this machine | Director's ruling, 2026-08-06; STEP-03 §3.1 |
| 3.1.3 | **GitHub-derived stats are version-anchored with per-count evidence links**; `projects.json` rewritten to promise exactly that | (a) run each external repo's suite in CI for genuinely live counts; (b) drop test counts entirely; (c) ship the existing "live count at build" string | Defect D-02: the GitHub API returns no test count. (a) is fragile — a broken external repo would break this site's build — and unverifiable by eye. Anchoring each count to a release tag or SHA plus a link to its source keeps the claim at the exact width of the evidence | Director's ruling, 2026-08-06. **Implemented P3.2** |
| 3.1.3a | **Deferred to v1.1:** each source repo's CI publishes a `stats.json` this site consumes at build, giving genuinely live counts without this site executing foreign test suites | Building it in v1.0 | Recorded as the forward path at the time the ruling was made, so v1.1 implements a decision rather than inventing one | Director's ruling, 2026-08-06 |
| 3.1.3b | **Recorded deviation from the frozen handoff.** Version anchors and evidence links change the truth strip (handoff §3) and the card (handoff §4) | Implementing §3/§4 literally | Charter-mandated: C-27 traceability and C-35 sourcing. Charter wins every conflict. Logged as a deviation rather than absorbed silently, per charter §8 | Director's ruling, 2026-08-06 |
| 3.1.4 | **v1.0.0 ships `VISITS —`; zero third-party resources** | Creating a GoatCounter account and wiring the counter | Defect D-03: GoatCounter publishes no stable SRI hash, so C-19 cannot fully cover it. The dash is already the designed state in handoff §3. Counter sits behind a one-line flag in `build.py` (`VISITS`) for later | Director's ruling, 2026-08-06 |
| 3.1.5 | **Charter Amendment 1** — C-33 scoped to contact-capable addresses; `users.noreply.github.com` exempt in commit metadata and in documentation of the git command | (a) checker allowlist with the exception noted only on /audit; (b) report C-33 UNMET; (c) keep the literal reading | Defect D-10: under a literal reading, committing at all makes C-33 permanently UNMET. Director's stated reason for amending over allowlisting: *the frozen text and the reported verdict must agree* — an exception noted only on /audit leaves the charter permanently contradicting its own MET claim | STEP-01-CHARTER.md, Amendment Log, Amendment 1 |
| 3.1.6 | **The ✓/✗ motif renders as a matched inline-SVG pair from one shared definition; ● is a CSS-drawn dot** | (a) substitute `×` U+00D7 for ✗; (b) SVG only for the two absent marks, ✓ stays a font glyph; (c) amend §5 to permit a third symbol face | Defect D-14: ✗ and ● exist in none of the five faces, and no X-mark variant exists in either family. Director's added condition: one definition, two marks, shared stroke-weight and size — so a future edit cannot drift one mark without the other. Enforced by the `MARK_SOURCE` and `MARK_DRIFT` gates | Director's ruling + addendum, 2026-08-06; `templates/_macros.html.j2` |
| 3.1.7 | **Both faces fetched from `google/fonts` OFL trees**, subset with fontTools 4.63.0 | IBM/plex upstream (`@ibm/plex-mono@2.5.0`) for Mono | One consistent licence tree publishing static instances at exactly the weights handoff §1 specifies. IBM/plex has moved to per-family releases and its latest release is Sans. Sources cited in `tools/subset_fonts.py`; upstream origin recorded there too | `tools/subset_fonts.py` header |
| 3.1.8 | **`font-display: swap` retained provisionally** | Dropping it now for preload-only | Handoff §6 bans it only *if it costs a Lighthouse point*, which is unmeasurable until P3.5 has the tooling. Director ruled: do not drop it blind. Carried as obligation O-8 | Director's ruling, 2026-08-06 |
| 3.1.9 | **Two numbering schemes kept:** `STEP-NN` for `docs/decisions/` files, `P3.x` for build phases, charter "Phase 3" for the whole build | Restating prior documents under one scheme | Raised as a conflict rather than guessed. Director ruled: declare the mapping once, no restatement | STEP-03 §"Numbering scheme" |
| 3.1.10 | **Output uses directory-style clean URLs** (`/projects/index.html` served as `/projects/`) | Flat `projects.html` | *Chosen by default; rationale not previously recorded.* **Retrospective:** gains clean canonical URLs for C-25 with no server config, which GitHub Pages cannot provide otherwise. Costs one extra directory level. Would choose again |
| 3.1.11 | **The colophon sentence lives in `build.py`, not in a data file** | Adding it to `profile.json` | Charter §5 fixes the sentence verbatim; it is charter-mandated site chrome, not portfolio content. C-34 governs portfolio content. Putting charter text into an owner-verified data file would trigger re-verification (O-3) for no gain. Recorded as reading R-03 | `build.py` `COLOPHON` |

### Unexamined defaults

Listed because a decision record that quietly omits its unexamined choices is a
record that flatters itself. Every tradeoff here is retrospective, written now.

| Choice | Alternative(s) | Status | Retrospective tradeoff |
|---|---|---|---|
| **Jinja2** as the template engine | Mako, string.Template, hand-rolled | Mandated in outline by charter §6A ("Python + templates"); the *choice of Jinja2 specifically* was never argued | Gains: `StrictUndefined` turns a missing data field into a build failure instead of a silent blank, which is exactly the C-34 guarantee. Autoescaping is on by default. Costs: one dependency. Would choose again |
| **sha256 truncated to 16 hex chars** for the determinism hash | Full digest; a manifest of per-file hashes | *Chosen by default; rationale not previously recorded.* | Gains: short enough for a human to compare two runs by eye, which is the actual use. Costs: not collision-proof — but this is a change-detector for the director, not a security control, and it should never be described as one |
| **`_site/` not committed** | Committing the built output | *Chosen by default.* | Gains: the deployed site is always a product of data + templates, so C-34 cannot be quietly violated by editing built HTML. Costs: the repo alone does not show what was served; the Action's artifact does |

## Phase P4.1: Signature motion (v1.1 amendment)

Design authority: `MOTION_SPEC_v1_1.md`. Contract: `STEP-08-P4.1-CONTRACT.md`.

| # | Decision | Alternative(s) not taken | Reason | Recorded in |
|---|---|---|---|---|
| 4.1.1 | **The C-10 lever's definition widens from "one variable" to "one mechanism: zeroed motion tokens, plus the animations that cannot be expressed as a token, all inside one block."** | (a) A second reduced-motion block beside the A3.6 rules; (b) a charter amendment to C-10 | The guarantee C-10 asks for is unchanged — one switch collapses all motion — and only the mechanism grew, so this is a design note and not an amendment. It is recorded because the widening is real: A3.5 is neutralised by zeroing `--motion-vt`, but A3.6 is scrubbed to scroll position and has no duration token to zero, so it is switched off by rule instead. Alternative (a) was refused twice over: a lever split across two blocks is two levers, and `check_animations.reduced_motion_body()` reads only the FIRST match, so a second block would be invisible to the gate that polices the condition | `MOTION_SPEC_v1_1.md` §A3.5; `tokens.css` lever block; owner ruling condition (2), 2026-08-10 |
| 4.1.2 | **Element selectors live in `tokens.css`, inside the lever block** | Keeping all element rules in `site.css` | A deliberate layering exception (reading R-14), taken only because 4.1.1's single-block requirement leaves nowhere else to put A3.6's kill rule. Recorded rather than left as an oddity for a reader to trip over | `tokens.css`; STEP-08 requirement 3.5 |
| 4.1.3 | **A3.5's duration is `var(--motion-vt)`, not the `250ms` literal the spec's code block shows** | Copying the spec's code block verbatim | The spec's own prose requires the token "so the lever below reaches it", which contradicts its illustrative code. Prose governs (reading R-13): the literal would put A3.5's duration permanently beyond the C-10 lever, which is the thing the surrounding paragraph exists to guarantee | `site.css` A3.5 block; `MOTION_SPEC_v1_1.md` §A3.5 |
| 4.1.4 | **`duration_type` is a closed enum of `ms \| scrubbed \| none`** | Two values, `ms \| scrubbed`, as the ruling literally specified | A3.2 is native scrolling with no duration at all. Typing it `ms` would attach a millisecond kind to something that has none, which is the invented value the same ruling forbids. Confirmed by the director at the P4.1 review stop: "each meaning what it says" | Owner ruling, P4.1 review stop, 2026-08-10; `test_duration_type_enum_is_closed` |
| 4.1.5 | **`check_reduced_motion` extended to inspect keyframe animations and `::view-transition-*`** | Leaving the two D-48 gates untouched and declaring the gap as an honest limit | The gate was proved BLIND by execution, not by argument: deleting `--motion-vt: 0ms` left A3.5 running at full 250ms under reduced motion while the checker printed "motion is switchable off (C-10)" and exited 0. Authorised by the director under condition (3)'s spirit — "the fence forbids weakening a gate to pass, not deepening one that passed vacuously." That exact sabotage is now the gate's permanent negative control | Owner ruling, P4.1 review stop; `check_animations.py` POISONED FIXTURE control |
| 4.1.6 | **A3.6's declaration lands in its own commit with its CSS, rather than the full six-item list landing with A3.5** | Literal compliance: declaring all six in the D2/D3 commit | Declaring an animation before its CSS exists makes the gate red — correctly, since that is the `UNSHIPPED_ANIMATION` direction working. Literal compliance would have forced D3 and D4 into one commit and deleted the review stop the same ruling ordered. The protected invariant is "the gate never lags its list at any commit", which this sequencing preserves at every commit. Deviation confirmed by the director at the review stop | Owner ruling, P4.1 review stop; commits `434c0b7`, this phase |

### Reversals

| What changed | From | To | Trigger |
|---|---|---|---|
| C-33's scope | Literal: no email address anywhere, unqualified | Contact-capable addresses only; noreply exempt in two named places | Defect D-10, found by reading before the first commit |
| `projects.json` count semantics | "live count fetched at build" | Version-anchored to a release/SHA, with an evidence link per count | Defect D-02, found by reading the data against what the GitHub API actually returns |
| Body-text floor in the shipped CSS | 12px, as `reference/design.html` renders it in 21 places | 12.5px, per handoff §1's own stated minimum | Defect D-12, found by tallying font declarations in the reference |
