# Defect log

Honest classification, per charter C-31. Every defect carries how it was found,
because that is the part that teaches: a defect found by reading is evidence the
review worked, and a defect found by running is evidence the reading was not
enough.

**Not logged:** syntax errors caught by the interpreter during authoring, within
the same edit cycle, that never reached a deliverable state. Logging those would
pad this file and make the counts here meaningless — which is the same
overclaiming the charter forbids elsewhere.

**Severity.** *Material* = would have shipped a false claim, a broken guarantee,
or an unreadable piece of evidence. *Minor* = real but caught with no downstream
cost.

---

## P3.1

| # | Defect | Found by | Severity | Disposition |
|---|---|---|---|---|
| D-01 | Global git identity was a routable, contact-capable address (redacted here per D-21 — it is not reproduced in this repo); it would have landed in every commit of a public repo, which C-33 bans, and commit authorship is immutable once pushed | **Reading** `git config` before any commit existed | Material | **Resolved.** Director ruled: set the GitHub noreply identity globally. Done before the first commit. See [DECISIONS](DECISIONS.md) 3.1.2 |
| D-02 | `projects.json` promised "live count fetched at build", but the GitHub API returns no test count. Shipping it would claim wider than the evidence | **Reading** the data against C-35 | Material | **Resolved by ruling**, implemented P3.2: counts version-anchored to a release/SHA, each with an evidence link; `projects.json` rewritten to promise exactly that. Genuinely-live counts recorded as the v1.1 path. DECISIONS 3.1.3 |
| D-03 | GoatCounter is the only third-party resource and publishes no stable SRI hash, so C-19 cannot fully apply to it | **Reading** C-19 against C-22 | Minor | **Resolved by ruling:** ship `VISITS —`; v1.0.0 carries zero third-party resources. DECISIONS 3.1.4 |
| D-04 | All four data files were marked `DRAFT — pending owner verification`, so C-27 could not report MET | **Reading** the data files | Material | **Resolved.** Director confirmed Phase 1 verification of 2026-08-05 with two named exceptions; `_status` lines rewritten accordingly (D5). Re-verification of D-02-rewritten fields is obligation O-3, owned by the P3.2 review stop |
| D-05 | The committed design is 100% inline `style=` attributes; C-18 bans inline scripts and a strict CSP wants `style-src 'self'` too | **Reading** `reference/design.html` against C-18 | Minor | **Resolved by default, enforced by gate.** Zero inline style and zero inline script from the first template; `build.py` refuses with `INLINE_STYLE` / `INLINE_SCRIPT`. P3.4's CSP work becomes a no-op rather than a rewrite |
| D-06 | A mobile hamburger nav would be a fourth animation, but handoff §5 closes the list at three | **Reading** handoff §5 against C-13 | Minor | **Deferred to P3.2** deliberately: nav wraps to a second line, CSS only, no JS, no animation. Intended semantics recorded here so P3.2 implements a decision rather than inventing one |
| D-07 | Every count in the design is a literal — `05 ENTRIES`, `ENTRIES 02`, `01 / 05`, `00 / 00` | **Reading** the design against C-34 | Material | **Resolved.** All counts render from `len(data)`. Verified in output: home shows `ENTRIES 02` derived from two `flagship: true` entries |
| D-08 | C-27 bans em-dashes in resume-derived text, but the frozen h1 and the charter's own colophon contain them, so a site-wide ban is impossible | **Reading** C-27 against the committed design | Minor | **Resolved by scoping:** the ban applies to `experience.json`, the rendered Experience page, and the PDF. All three verified clean already (PDF: 0 em-dashes across 6,988 extracted chars). Checker lands in P3.2 |
| D-09 | No OG image or favicon exists, but C-25 requires "a real OG image" | **Reading** C-25 against the asset inventory | Minor | **Deferred to P3.2.** Generated deterministically from tokens with Pillow — nothing hand-drawn |
| D-10 | C-33 bans an email address in "metadata" and "commit-published files" without qualification, so committing at all would make C-33 permanently UNMET — including under D-01's fix | **Reading**, pre-first-commit | Material | **Resolved by charter Amendment 1** (2026-08-06): C-33 scoped to contact-capable addresses; `users.noreply.github.com` exempt in commit metadata and in documentation of the git command. Director chose amendment over checker-allowlist so the frozen text and the reported verdict agree |
| D-11 | A phone-shaped regex matches ISO-8601 dates (`2026-08-06`), producing false positives | **Running** the pre-commit scan | Minor | **Deferred to P3.2**, specified: `check_c33.py` excludes ISO-8601 shapes and ships a positive-control fixture full of dates that must not trip it. A checker that cries wolf on every date is a checker that gets ignored |
| D-12 | `reference/design.html` renders body and evidence text at 12px in 21 places, below handoff §1's own stated floor of "body ≥12.5px" | **Reading**, by counting font declarations | Minor | **Resolved.** Handoff §1 wins over design.html per BUILD_KICKOFF (handoff wins every visual question; design.html is reference, never shipped code). `--type-mono-body-sm` sets the floor at 12.5px. Recorded as reading R-01 |
| D-13 | This machine's console is cp1252; any script printing `✓ → —` crashes with `UnicodeEncodeError`, so every build tool would fail on its own evidence output | **Running** the glyph scan | Material | **Resolved.** Every tool pins `sys.stdout`/`stderr` to UTF-8 and writes files with explicit `encoding="utf-8"` |
| D-14 | `✗` (U+2717) and `●` (U+25CF) exist in **none** of the five shipped faces, and no X-mark variant exists in either family. Left as text they fall back to a system symbol font: a third typeface, different per OS, failing silently with all tests green — and the ✓/✗ pair is the site's motif | **Running** a cmap probe over the downloaded fonts | **Material** | **Resolved by ruling:** matched inline-SVG pair + CSS dot, from a single shared definition (`_mark`) so no edit can drift one mark without the other. Enforced by `MARK_SOURCE` and `MARK_DRIFT` gates. DECISIONS 3.1.6 |
| D-15 | Count expressions were written `'%02d' % projects \| length`; Jinja binds `\|` looser than `%`, so this formats the list and then takes the *string's* length — silently rendering a wrong count | **Reading** my own templates before running them | Material | **Fixed** by parenthesising: `'%02d' % (projects \| length)`. Would have shipped a wrong number on four pages in the one place C-34 is most visible |
| D-16 | `subset_fonts.py --report` printed five columns all truncated to `InstrumentS` / `IBMPlexMono`, making the coverage matrix — the phase's key evidence — impossible to read | **Reading** the tool's own output | Minor | **Fixed.** Columns now short-labelled `IS-Regular`, `PM-SemiBold` etc. Evidence the director cannot read is not evidence |

| D-17 | The commit-message convention appends `Co-Authored-By: … <noreply@anthropic.com>`, an email address in commit-published metadata. Amendment 1 exempted only `users.noreply.github.com`, so the first commit would have put C-33 straight back into violation | **Reading** the commit convention against Amendment 1, before the first commit | Material | **Resolved by charter Amendment 2:** exemptions stated as an enumerated list with an explicit purpose clause, not a pattern. Director's condition: `noreply@` at any *unlisted* domain must still trip the checker — which is what proves the implementation enumerates rather than pattern-matches |
| D-18 | Both font tests read `build/fonts-src/*.ttf`, which is **gitignored**. Three faults in one: (a) they passed locally only because the downloads happened to be present, so **the suite's pass/fail and its count were environment-dependent — and that count is destined for /audit**, where a number that changes with the machine is not evidence; (b) they asserted a property of the *upstream* font rather than of the shipped subset, so a subsetting bug that dropped a glyph would not have failed them; (c) the negative control asserted `0x2717 not in <a real font>`, testing a property of the fixture rather than the gate's behaviour, and would have failed for the wrong reason had that glyph ever been added | **Running** — the first CI run, which had no `build/fonts-src`. Independently identified by the director from the same log | **Material** | **Fixed in two parts.** Positive control now uses `shipped_coverage()` against `assets/fonts/*.woff2` — committed, and what visitors actually download. Negative control now drives the extracted pure gate `find_gaps()` with a **synthetic** cmap: build a complete set, remove one required codepoint, assert exactly that gap is found. No files, no network, identical result and identical count on any machine |

---

## P3.2

| # | Defect | Found by | Severity | Disposition |
|---|---|---|---|---|
| D-19 | `gate_color_literal` refused the numeric HTML entity `&#8599;` (the ↗ arrow) as `REASON=COLOR_LITERAL`. By shape a 4-digit entity is indistinguishable from a `#RGBA` hex colour. **A false refusal is as much a gate defect as a false pass** — it just fails loudly instead of quietly | **Running** the build on the first real templates | Minor | **Fixed.** Negative lookbehind on `&` discriminates entity from colour; regression test asserts entities pass *and* that the real 4-digit hex form still refuses. The macro also switched to the literal `↗`, which is in the subset |
| D-24 | Once `check_c33.py` became git-tracked, the scan covered it — and its own poisoned fixtures are by construction exactly what it exists to find, so **the checker failed itself**. It passed locally only because the file was still untracked when I ran it: a third form of state-dependent behaviour in this phase | **Running** — CI, third time | Material | **Fixed without an exclusion.** Excluding the checker's own path was the easy fix and the wrong one: it creates a permanent blind spot where a real address could sit unscanned. Fixtures are now assembled from fragments at runtime, so **no contact-shaped literal exists anywhere in the repo**, and the checker scans itself with zero exclusions while still proving all 16 controls |
| D-23 | `pdfminer.six` was absent from `requirements.txt`. It was installed locally, so the PDF half of the C-33 scan — required by contract 3.5 — ran here and **crashed in CI**. Second occurrence of the D-18 pattern: an unpinned local dependency making a check environment-dependent | **Running** — CI, again | Material | **Fixed.** Pinned at `20260107`. The recurrence is itself the finding: local success is not evidence about CI, and this build has now produced that lesson twice |
| D-21 | `docs/DEFECTS.md` reproduced the old routable address verbatim while documenting D-01 — **the defect log about a leaked address leaked the address**. Committed and pushed before `check_c33.py` existed to catch it | **Running** `check_c33.py` for the first time | **Material** | **Redacted** in the working tree; D-01's entry now describes the address without reproducing it. **Honest limit: the string remains in published git history** (commit `e967e22`) and can only be removed by rewriting public history. Raised to the director as a decision, not fixed unilaterally |
| D-22 | The em-dash check, scoped to "the rendered Experience page", flagged site chrome shared by all five pages: the `<title>` separator and the footer's `VISITS —`. The latter is the **handoff-mandated designed state**, so enforcing the rule as written would have forced a change that violates the design authority | **Running** the checker against real output | Minor | **Fixed by narrowing scope to `<main>`** — where resume-derived text actually lives. Chrome *inside* `<main>` is still bound, which is the point. Both cases locked in as controls |
| D-20 | One test conflated two conditions: it checked `src` and `href` together against a single allowlist, so it flagged `mohdsaifhussain.github.io` — **the site's own origin** — as third-party. C-04/C-19 govern *loaded resources*; C-20 governs *outbound navigation* | **Running** the suite against the first real content | Minor | **Fixed.** Split into `test_no_third_party_resources_load` (fetched resources must be same-origin relative paths) and `test_outbound_links_are_allowlisted` (navigation destinations enumerated explicitly, own origin included by name) |

Five further defects (F-01 to F-05) were found in the adversarial pass at the
P3.1 review stop, against code written the same session; they are recorded in
STEP-03's outcome rather than here, because none of them ever left the phase.

**P3.1 totals, counted from the rows above:** 18 logged — **13 found by reading**
source, docs or data (D-01 to D-10, D-12, D-15, D-17), **5 found by running** a
tool and reading its output (D-11, D-13, D-14, D-16, D-18). **10 material,
8 minor.**

Worth keeping in view: every defect that would have shipped a false or broken
claim was caught before the site was ever served — D-14 (the motif silently
falling back to a third typeface), D-15 (a wrong count on four pages),
D-01/D-10/D-17 (a published email address, three separate times), D-18 (a test
measuring the wrong artifact). **None of them would have been caught by a green
test suite**: D-18 *was* a green test suite, passing for the wrong reason. Five
were found only because a tool was run and its output read by eye.
