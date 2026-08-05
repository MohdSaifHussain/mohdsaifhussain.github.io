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

### Reversals

| What changed | From | To | Trigger |
|---|---|---|---|
| C-33's scope | Literal: no email address anywhere, unqualified | Contact-capable addresses only; noreply exempt in two named places | Defect D-10, found by reading before the first commit |
| `projects.json` count semantics | "live count fetched at build" | Version-anchored to a release/SHA, with an evidence link per count | Defect D-02, found by reading the data against what the GitHub API actually returns |
| Body-text floor in the shipped CSS | 12px, as `reference/design.html` renders it in 21 places | 12.5px, per handoff §1's own stated minimum | Defect D-12, found by tallying font declarations in the reference |
