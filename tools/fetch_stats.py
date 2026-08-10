"""Fetch GitHub-derived facts at build time.  P3.2 / D6.

Charter C-35: GitHub-derived stats are fetched at build time — never
client-side — snapshotted with a visible "as of" timestamp, and sourced per
C-27.

WHAT THIS DOES NOT DO, and why that matters (defect D-02)
The GitHub REST API does not return a test count. It never has. `projects.json`
previously promised a "live count fetched at build", which was a claim wider
than any evidence this tool could produce. Per the director's ruling
(DECISIONS 3.1.3) this tool fetches what the API genuinely provides — the
release tag or commit SHA each repo currently sits at, and when it was last
pushed — and every displayed count is anchored to that and linked to its
source. The counts themselves remain resume-stated baselines, labelled as such.

Genuinely live counts are recorded as the v1.1 path (DECISIONS 3.1.3a): each
source repo's own CI publishes a stats.json this site consumes. That is NOT
built here, and this tool must not pretend otherwise.

SEPARATION OF CONCERNS (contract 3.2)
build.py NEVER reaches the network. This tool is run explicitly — by the
weekly scheduled Action, or by hand — and writes a committed snapshot that the
build reads. A build that fetches is neither deterministic nor reproducible
offline, and P3.1's cross-platform hash guarantee would be lost.

Usage (PowerShell):
    python tools\\fetch_stats.py
    python tools\\fetch_stats.py --check      # report staleness, fetch nothing
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")     # defect D-13
sys.stderr.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROJECTS = ROOT / "data" / "projects.json"
OUT = ROOT / "data" / "generated" / "github.json"

API = "https://api.github.com"
OWNER = "MohdSaifHussain"

# Q2 ruling: staleness never fails the build; warn above this, in build output
# only. The page always carries its honest "as of" date regardless.
STALE_DAYS = 21


def _get(url: str) -> dict | None:
    """GET with the Actions token when present. 404 is a real answer, not an
    error: most of these repos have no releases, and that is the fact we want."""
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "mohdsaifhussain.github.io-build",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def _get_text(url: str) -> str | None:
    """Plain GET for a raw file. 404 means the repo publishes no stats.json,
    which is a fact about that repo rather than a failure here."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "mohdsaifhussain.github.io-build",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def repo_names() -> list[str]:
    """Derived from projects.json, never hardcoded — so adding a project to the
    data file is genuinely the only step (C-34)."""
    data = json.loads(PROJECTS.read_text(encoding="utf-8"))
    names: list[str] = []
    for project in data["projects"]:
        for url in project.get("links", {}).values():
            prefix = f"https://github.com/{OWNER}/"
            if url.startswith(prefix):
                name = url[len(prefix):].strip("/")
                if name and name not in names:
                    names.append(name)
    return names


def anchor_for(repo: str) -> dict:
    """The version anchor: a release tag where one exists, else the commit SHA
    the default branch currently sits at. Both are citable; neither is a count."""
    release = _get(f"{API}/repos/{OWNER}/{repo}/releases/latest")
    meta = _get(f"{API}/repos/{OWNER}/{repo}")
    if meta is None:
        raise SystemExit(f"REASON=REPO_NOT_FOUND  {OWNER}/{repo}")

    if release:
        return {
            "anchor": release["tag_name"],
            "anchor_type": "release",
            "anchor_url": release["html_url"],
            "pushed_at": meta["pushed_at"],
            "repo_url": meta["html_url"],
        }

    branch = _get(f"{API}/repos/{OWNER}/{repo}/commits/{meta['default_branch']}")
    sha = branch["sha"]
    return {
        "anchor": sha[:7],
        "anchor_type": "commit",
        "anchor_url": f"{meta['html_url']}/commit/{sha}",
        "pushed_at": meta["pushed_at"],
        "repo_url": meta["html_url"],
    }


RAW = "https://raw.githubusercontent.com"


def stats_url(repo: str) -> str:
    return f"{RAW}/{OWNER}/{repo}/main/stats.json"


def ci_stats(repo: str) -> dict | None:
    """The CI-published test count, if this repo publishes one.

    DEFECT D-02'S RECORDED UPGRADE PATH, implemented 2026-08-10. The GitHub API
    returns no test count, so every displayed figure was a RESUME-STATED
    BASELINE anchored to a version. The recorded v1.1 path (DECISIONS 3.1.3a)
    was: each source repo's CI publishes a stats.json this site consumes, so the
    figure becomes measured rather than asserted.

    ABSENCE IS NOT FAILURE. A repo that publishes no stats.json keeps its
    resume-stated baseline, and the card says which basis it is on. Returning
    None here is the honest outcome, not an error — the same rule write_audit.py
    follows for scores.

    WHAT IS NOT TRUSTED. The count is used only if the payload carries a commit
    and a measurement timestamp, so a figure can never render without the anchor
    and the as-of that make it checkable. A count with no provenance is exactly
    the unanchored claim D-02 was about.
    """
    raw = _get_text(stats_url(repo))
    if raw is None:
        return None
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError:
        print(f"  {repo:<24} stats.json present but not valid JSON — ignored")
        return None

    required = ("tests_executed", "commit", "measured_at")
    if not all(doc.get(k) for k in required):
        print(f"  {repo:<24} stats.json missing {required} — ignored")
        return None
    if not isinstance(doc["tests_executed"], int) or doc["tests_executed"] <= 0:
        print(f"  {repo:<24} stats.json reports a non-positive count — ignored")
        return None

    return {
        "tests_executed": doc["tests_executed"],
        "tests_passed": doc.get("tests_passed"),
        "tests_skipped": doc.get("tests_skipped"),
        "tests_failed": doc.get("tests_failed"),
        "commit": doc["commit"],
        "commit_short": doc["commit"][:7],
        "commit_url": f"https://github.com/{OWNER}/{repo}/commit/{doc['commit']}",
        "measured_at": doc["measured_at"],
        "run_url": doc.get("run_url"),
        "runner": doc.get("runner"),
        "source_url": stats_url(repo),
    }


def age_days(snapshot: dict) -> float:
    as_of = dt.datetime.fromisoformat(snapshot["as_of"].replace("Z", "+00:00"))
    return (dt.datetime.now(dt.timezone.utc) - as_of).total_seconds() / 86400


def verify_links() -> int:
    """Every evidence link in the snapshot must actually resolve.

    Director's ruling 2026-08-06: resolvability checking belongs HERE, in the
    weekly networked job, not in the build. The build stays hermetic (contract
    3.2) and a link that dies later is caught by machinery within a week rather
    than by the owner's eye.

    An anchor is a claim: "this figure was stated at this version, and here is
    the proof". A claim whose proof 404s is worse than no claim, because it
    looks checkable and is not.
    """
    if not OUT.exists():
        print(f"REASON=SNAPSHOT_MISSING  {OUT.relative_to(ROOT)}")
        return 1
    snap = json.loads(OUT.read_text(encoding="utf-8"))

    failures = []
    for name, r in sorted(snap["repos"].items()):
        # The CI-measured entries carry two more claims: the commit the count
        # was measured at, and the stats.json it came from. Both are evidence
        # links in exactly the sense this function exists for, so both are
        # checked. A measured figure whose source 404s is worse than a baseline,
        # because it looks more checkable and is not.
        fields = ["anchor_url", "repo_url"]
        if r.get("stats"):
            fields += ["commit_url", "source_url"]

        for field in fields:
            url = r.get(field) or (r.get("stats") or {}).get(field)
            if not url:
                failures.append((name, field, "missing"))
                continue
            req = urllib.request.Request(url, method="HEAD", headers={
                "User-Agent": "mohdsaifhussain.github.io-linkcheck"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    code = resp.status
            except urllib.error.HTTPError as e:
                code = e.code
            except Exception as e:                        # noqa: BLE001
                code = f"ERR {e}"
            ok = code == 200
            print(f"  {'OK ' if ok else 'DEAD'}  {code:<6} {name:<24} {field}")
            if not ok:
                failures.append((name, field, code))

    if failures:
        print("\nEVIDENCE LINK CHECK FAILED")
        for name, field, code in failures:
            print(f"  REASON=DEAD_EVIDENCE_LINK  {name}.{field} -> {code}")
        return 1
    print("\nEVIDENCE LINKS OK — every anchor and repo URL resolves")
    return 0


def check() -> int:
    if not OUT.exists():
        print(f"REASON=SNAPSHOT_MISSING  {OUT.relative_to(ROOT)} has never been fetched")
        return 1
    snap = json.loads(OUT.read_text(encoding="utf-8"))
    days = age_days(snap)
    print(f"snapshot as of {snap['as_of']}  ({days:.1f} days old)")
    for name, r in sorted(snap["repos"].items()):
        print(f"  {name:<24} {r['anchor']:<10} {r['anchor_type']}")
    if days > STALE_DAYS:
        print(f"\nWARNING  snapshot is older than {STALE_DAYS} days. "
              f"Not a failure: the page carries its honest 'as of' date.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true",
                    help="report snapshot staleness without fetching")
    ap.add_argument("--verify-links", action="store_true",
                    help="confirm every evidence link in the snapshot resolves")
    args = ap.parse_args()
    if args.check:
        return check()
    if args.verify_links:
        return verify_links()

    now = dt.datetime.now(dt.timezone.utc)
    repos = {}
    for name in repo_names():
        repos[name] = anchor_for(name)
        stats = ci_stats(name)
        if stats:
            repos[name]["stats"] = stats
        r = repos[name]
        measured = (f"  CI-measured {stats['tests_executed']} tests @ "
                    f"{stats['commit_short']}") if stats else "  resume baseline"
        print(f"  {name:<24} {r['anchor']:<10} ({r['anchor_type']}){measured}")

    snapshot = {
        "_generated": ("Machine-written by tools/fetch_stats.py. Never hand-edited. "
                       "Anchors are release tags or commit SHAs fetched from the "
                       "GitHub API; they are NOT test counts — the API returns no "
                       "test count (defect D-02, DECISIONS 3.1.3)."),
        "as_of": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "as_of_display": now.astimezone(
            dt.timezone(dt.timedelta(hours=5, minutes=30))
        ).strftime("%Y-%m-%d %H:%M IST"),
        "repos": repos,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8", newline="\n")
    print(f"\nwrote {OUT.relative_to(ROOT)}  as of {snapshot['as_of_display']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
