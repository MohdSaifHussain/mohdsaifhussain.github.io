# SOP — maintaining this site

**C-36.** Written for Windows and PowerShell 5.1. Every command here is safe to
paste as-is: `;` and `if ($?)`, never `&&`.

**Updating the site means editing one data file and pushing.** No HTML is ever
edited to change content (C-34). If a change seems to need a template edit, that
is a design change, not a content update.

> **Provenance of this manual.** Every procedure below was **performed by the
> builder, end to end** — edit, gates, deploy, verify, revert — under the owner's
> direction of 2026-08-06, with walkthrough artefacts labelled and removed. The
> owner's own walkthrough is **deferred and declared**, in the same manner as
> C-08's screen-reader partial. So these steps are proven to *work*; they are not
> yet proven to be *followable by the owner unaided*. That distinction is the
> point of C-36 and is not glossed here.
>
> **Narrowed 2026-08-22.** On 2026-08-22 the owner directed two additions
> through the procedure end to end (Switchyard added, TS-Sentry re-sourced;
> DECISIONS CU-1 to CU-4), which narrows the declaration without faking it:
> the owner ruled on every step and read every result, and the builder typed
> the commands. "Unaided" remains undemonstrated and is still declared.

---

## Before anything: the one command that checks everything

```powershell
python build.py;                   "build exit=$LASTEXITCODE"
python -m pytest;                  "tests exit=$LASTEXITCODE"
python tools\check_c33.py;         "c33 exit=$LASTEXITCODE"
python tools\check_content.py;     "content exit=$LASTEXITCODE"
python tools\check_animations.py;  "animations exit=$LASTEXITCODE"
python tools\check_contrast.py;    "contrast exit=$LASTEXITCODE"
```

All six must print `exit=0`. **Read the exit codes, not the last line of output** —
a defect in this build (D-39) came from filtering output and hiding a failure.

---

## 1. Add a new project

1. Open `data\projects.json`. Copy an existing entry and edit it.
2. Required: `id`, `name`, `problem`, `method`, `verified_metrics`, `links.repo`.
   `links.repo` **must** be a real GitHub URL — the build refuses a project it
   cannot anchor (`REASON=STAT_UNANCHORED`).
3. Refresh the anchor so the new repo gets a version:
   ```powershell
   python tools\fetch_stats.py
   ```
4. Run the six checks above, then:
   ```powershell
   git add data\projects.json data\generated\github.json
   git commit -m "content: add <project name>"
   git push
   ```
5. CI builds, gates, and deploys. Confirm at <https://mohdsaifhussain.github.io/projects/>.

Counts update themselves — `05 ENTRIES`, the `01 / 05` positions, the home
flagship count. Never type a number.

**Order is automatic (P5.5).** Entries render newest push first on Projects
and Home, from the snapshot's `pushed_at`, so the position of an entry in
`projects.json` does not matter; step 3 is what gives the new entry its
date, and the build refuses (`REASON=PUSH_DATE_MISSING`) if it is skipped.

## 1a. Add or change a project's architecture diagram

1. Open `tools\gen_diagrams.py`. Each diagram is a function: nodes with the
   README's own labels, edges between them, explicit `label_at` positions
   for edge labels. Add a function and append it to `DIAGRAMS`.
2. Generate. The generator **refuses** a drawing in which any text overlaps a
   node or another text, and names the pair:
   ```powershell
   python tools\gen_diagrams.py;   "diagrams exit=$LASTEXITCODE"
   ```
   Move the named label (`label_at`) or node until it prints `DIAGRAMS OK`.
3. In `data\projects.json`, set the entry's `diagram` to the function's name
   and `diagram_source` to the README lines it was transcribed from.
4. Never edit a file under `templates\diagrams\` by hand: the test suite
   compares each one to the generator's output and fails on any difference.
5. Six checks, commit `tools\gen_diagrams.py`, `templates\diagrams\`,
   `data\projects.json`, push.

## 2. Add a certification or completed course

1. Open `data\certifications.json`, add an entry to `certifications`:
   `issuer`, `course`, `completed` (YYYY-MM), `verify_url`, `public`.
2. **Only entries with a real verification URL, or an honest
   `no_public_verification: true`, are accepted** (C-27).
3. When the first real entry lands, delete the `status_note` field — the empty
   state retires with it.
4. Six checks, then commit and push as above.

## 3. Edit profile or experience data

1. `data\profile.json` or `data\experience.json`.
2. **`experience.json` must never contradict the web-resume PDF** (C-29), and
   is inside the em-dash ban (C-27) — `check_content.py` enforces it.
3. Six checks, commit, push.

## 4. Replace the web-resume PDF

1. Strip email and phone from the PDF **before** copying it in. The web version
   carries LinkedIn only (C-33).
2. Overwrite `assets\resume\MohdSaifHussain_Resume_Web.pdf`.
3. **Re-scan — this is not optional:**
   ```powershell
   python tools\check_c33.py;  "c33 exit=$LASTEXITCODE"
   ```
   Exit 0 means no contact-capable address and no phone number in the repo or in
   the PDF's extracted text. Anything else: fix the PDF, do not proceed.
4. Confirm it still agrees with `experience.json` (C-29). Commit and push.

## 5. Pre-release checklist

```powershell
# 1. Everything green locally
python build.py; python -m pytest
python tools\check_c33.py; python tools\check_content.py
python tools\check_animations.py; python tools\check_contrast.py

# 2. Refresh the anchors and confirm every evidence link still resolves
python tools\fetch_stats.py
python tools\fetch_stats.py --verify-links;  "links exit=$LASTEXITCODE"

# 3. Push, then measure the PUBLISHED site under the protocol
gh workflow run measure-live.yml
gh run list --workflow=measure-live.yml --limit 1

# 4. Read the measured numbers and update declarations if any changed
start https://mohdsaifhussain.github.io/audit/
```

**Scores publish exactly as measured.** If a number is worse, it is published
worse and the condition is declared UNMET with that number. Re-running for a
better figure is forbidden — the protocol is median-of-3 precisely so a single
unlucky run is not the answer, and so a lucky one is not either.

## 6. File a charter amendment

The charter text is frozen. Changes are **appended** as numbered amendments;
the original is never edited.

1. Open `docs\decisions\STEP-01-CHARTER.md`, go to the Amendment Log.
2. Add the next number with: date, who filed it, which condition it amends,
   status, the amendment text, the **reason**, why amending rather than working
   around it, and how it is verified.
3. If a checker enforces the amended condition, update it **and its controls**
   in the same commit. An amendment whose checker still enforces the old text is
   worse than no amendment.
4. Cite the amendment by number wherever the condition is reported on /audit.

Worked examples: Amendments 1 and 2, both about C-33.

---

## If the build refuses

It prints `REASON=<CODE>` and a detail line. The codes are deliberate:

| Code | Meaning |
|---|---|
| `DATA_MISSING` / `DATA_MALFORMED` | a data file is absent or is not valid JSON |
| `STAT_UNANCHORED` | a project cannot render both a version anchor and an evidence link |
| `ASSET_REF_MISSING` | a page references a file that is not there |
| `COLOR_LITERAL` / `TOKEN_UNKNOWN` | a colour was written outside `tokens.css` |
| `INLINE_STYLE` / `INLINE_SCRIPT` | markup that would breach the CSP |
| `MARK_SOURCE` / `MARK_DRIFT` | the ✓/✗ pair stopped sharing one definition |
| `EMAIL_FOUND` / `PHONE_FOUND` | C-33 |
| `EM_DASH` / `COUNT_LITERAL` | resume-derived em-dash, or a typed count |
| `UNDECLARED_ANIMATION` / `UNSHIPPED_ANIMATION` | motion and `audit-spec.json` disagree |

**A refusal is the system working.** Fix the cause; never bypass the gate.
