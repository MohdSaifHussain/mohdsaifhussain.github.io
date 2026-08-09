---
description: Post-release deviation audit — verify the released site by execution, findings only, no remediation
---

# Deviation audit

Audit the released site against its own record. **Findings only.** Do not fix
anything, do not change any state, do not push. Compile one report and stop.

Verify by **execution**, not by reading. Every item below has a command that
produces evidence; run it and quote what it printed. A claim in a document is
the thing being audited, never the evidence for it.

## Standing rules

- **A green job is not evidence that its output reached the page.** This is the
  single most productive question in this repository's history — D-45, D-46 and
  D-47 were all instances of it, and every one was invisible in the job logs.
- Compare **served bytes** against **built bytes**. Neither alone has ever
  caught anything; the comparison has caught several.
- **Check the clock in UTC.** Cron in GitHub Actions is UTC. The workstation is
  IST (+05:30), so for 5.5 hours a day the local date is one day ahead and a
  scheduled run can look overdue when it is hours away. Establish `date -u`
  before concluding anything about a schedule.
- Absence of a run is not evidence of a missed run. Confirm the schedule was
  actually due before calling it a failure.
- Read **exit codes**, never the last line of output (D-39).

---

## 1. Tag integrity and post-release history

```bash
git fetch --all --tags --prune
git rev-parse v1.0.0^{commit}          # must equal the recorded release SHA
git cat-file -t v1.0.0                 # must be: tag  (annotated, unsigned)
git reflog show v1.0.0                 # any output = the tag has been moved
git ls-remote --tags origin            # remote must agree with local
git log --oneline v1.0.0..origin/main
git diff v1.0.0 HEAD --stat            # what has actually changed since release
```

List every commit since the tag with **author and purpose**. Bot commits are
expected (`github-actions[bot]`); a human commit nobody mentioned is a finding.

## 2. CI status

```bash
gh run list --branch main --limit 20
```

Most recent runs on `main`, with conclusions. Note any failure that is not
superseded by a later green run on a later SHA.

## 3. Scheduled workflows — did they fire, and **did their output deploy?**

This is the section this repository keeps failing, so it gets the most scrutiny.

```bash
date -u                                             # establish UTC first
gh run list --workflow refresh-stats.yml --limit 10
gh run list --workflow measure-live.yml  --limit 10
```

For each scheduled workflow:

1. **Was it due?** Compute the next cron firing in UTC and compare to `date -u`.
   Not-yet-due is not a defect.
2. **Did it run, and did it pass?** Exit code, not colour alone.
3. **Did it commit?** `git log --author=github-actions`
4. **DID THE COMMIT ACTUALLY DEPLOY?** — the question that matters:

```bash
# A deploy triggered by a bot push does NOT exist. GitHub suppresses workflow
# triggers for pushes made with the default GITHUB_TOKEN, so the job must
# dispatch the deploy explicitly. Confirm a dispatched run exists for the bot
# commit, and that it succeeded:
gh run list --workflow deploy.yml --limit 5 \
  --json databaseId,event,conclusion,headSha \
  --jq '.[] | "\(.databaseId) \(.event) \(.conclusion) \(.headSha[0:7])"'
```

A bot commit SHA with **no `workflow_dispatch` deploy run against it** means the
measurement or snapshot never reached the site. That is D-45/D-46, and it is
silent: the rendered "as of" stamp stays consistent with the stale data it is
rendering, so no visitor sees anything wrong and the refresh simply stops
meaning anything.

Then confirm the machinery *can* work, which is not the same question:

```bash
# D-47: declaring a permissions block sets every unlisted scope to `none`, so a
# job that dispatches must declare actions: write or the dispatch 403s. A
# dispatch step that has never run is not a working dispatch step.
grep -A4 '^permissions:' .github/workflows/*.yml
grep -n 'gh workflow run' .github/workflows/*.yml
```

Also confirm the single-path guard still constrains the bot to its one file, and
that no tooling by-product (`vnu.json`, `axe.json`, `gates.json`,
`.lighthouseci/`, `node_modules/`) is untracked-and-unignored, which would trip
the guard and fail the job.

## 4. Evidence links

```bash
python tools/fetch_stats.py --verify-links
```

Report every link with its status code, and the exit code.

## 5. Animation gate

```bash
python tools/check_animations.py
python tools/check_animations.py --selftest
```

Then verify **independently of the checker** — a gate cannot be its own evidence:

```bash
grep -nE '@keyframes|animation[-:]|transition[-:]|scroll-behavior|translate|rotate|scale\(' _site/css/*.css
grep -nE 'scroll-snap|overflow-x|prefers-reduced-motion' _site/css/*.css
grep -nE 'scroll|wheel|touchmove' static/js/*.js
```

Confirm the declared list is exactly what `data/audit-spec.json` says, that both
directions are green, and that no undeclared motion ships.

## 6. /audit is current, and every cell has a producer

```bash
git log --oneline -- data/generated/audit.json      # author must be the bot
python -c "import json,io;d=json.load(io.open('data/generated/audit.json',encoding='utf-8'));print(d['as_of'],d['measured_against']);print(sorted(d['measured']));print(sorted(d.get('gates',{}).get('results',{})))"
```

Then the check that matters — **served vs built**:

```bash
python build.py
for p in "" projects/ experience/ certifications/ audit/; do
  curl -s "https://mohdsaifhussain.github.io/$p" -o /tmp/s.html
  echo "$p $(sha256sum /tmp/s.html | cut -c1-16) $(sha256sum _site/${p}index.html | cut -c1-16)"
done
```

**Count the `— AT DEPLOY` cells on the live page.** That string means "nothing
has produced this cell yet". On a released site it should be zero. D-48 was nine
of them sitting there for a whole release under a footnote claiming CI measured
them — every gate green, nothing broken, the page simply under-reporting itself.

```bash
curl -s https://mohdsaifhussain.github.io/audit/ | grep -c 'AT DEPLOY'
python tools/gate_status.py --selftest    # the producers must be able to FAIL
```

For any cell that is empty, ask the D-48 question: **is there a writer, and is
it actually invoked?** A flag that exists and is passed by nothing is not a
writer. Check the call site, not the argument parser.

## 7. Displayed figures vs the data

Spot-check the rendered pages against `data/*.json` — truth strip against
`profile.json`, project cards and metrics against `projects.json`, anchors
against `data/generated/github.json`. Confirm counts are derived, never typed
(`check_content.py` enforces `COUNT_LITERAL`).

## 8. The full local gate set (SOP.md)

```powershell
python build.py;                   "build exit=$LASTEXITCODE"
python -m pytest;                  "tests exit=$LASTEXITCODE"
python tools\check_c33.py;         "c33 exit=$LASTEXITCODE"
python tools\check_content.py;     "content exit=$LASTEXITCODE"
python tools\check_animations.py;  "animations exit=$LASTEXITCODE"
python tools\check_contrast.py;    "contrast exit=$LASTEXITCODE"
```

All six must print `exit=0`. Report the codes. Confirm `git status` is clean
afterwards — the build must not have dirtied a tracked file.

## 9. Open items

Sweep `docs/DECISIONS.md`, `docs/DEFECTS.md` and `docs/decisions/STEP-*.md` for
anything still awaiting a ruling. For each obligation `O-n`, find where it was
discharged or closed by decision. Distinguish:

- **genuinely open** — needs an owner ruling;
- **closed** — discharged, with the record naming what closed it;
- **open by declaration** — carried deliberately and published on /audit
  (C-08's four unverified pages, A4.7's historical commit, v1.1 deferrals);
- **stale marker** — closed in the record, still described as pending somewhere
  else. Findings 9a and 9b were both this. Same class as D-37.

Grep the data files too, not just the docs — a stale "pending" note in
`profile.json` outlived its obligation by four days.

---

## Report

Findings first, each with the command that produced it and what that command
printed. Severity, and whether it is time-sensitive. Then propose remediations
**only where a finding requires one**, and stop for the owner's ruling before
touching anything.

State plainly what was clean. An audit that reports only problems gives no
information about coverage.

If a premise in the request turns out to be wrong — a run that was not actually
due, a defect already closed — **say so and show the evidence**. Correcting the
question is a finding.
