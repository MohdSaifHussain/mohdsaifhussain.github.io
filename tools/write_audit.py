"""Merge measured results into data/generated/audit.json.  P3.5 / D3.

C-30 and C-35: /audit publishes what was MEASURED. This is the only writer of
audit.json, and it writes only values produced by a tool.

THE RULE THIS ENFORCES (contract 3.1, 3.2)
  - a value with no tool output is ABSENT, never a placeholder and never a
    guess. /audit then renders "— AT DEPLOY", which is honest;
  - a score is written exactly as measured. There is no rounding up, no
    "best of N", no re-run for a better number. Requirement 3.2 forbids it and
    Q2(c) was placed on the record as refused.

So the failure mode this tool is built against is not a crash. It is a
plausible number appearing where no measurement happened.

Usage (CI):
    python tools/write_audit.py --lighthouse .lighthouseci --vnu vnu.json \\
                               --axe axe.json
    python tools/write_audit.py --selftest
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import statistics
import subprocess
import sys
import tempfile
import urllib.parse

sys.stdout.reconfigure(encoding="utf-8")     # defect D-13
sys.stderr.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "generated" / "audit.json"


def lighthouse_scores(lhci_dir: pathlib.Path) -> dict:
    """Lowest score per category across every page and profile.

    The LOWEST, deliberately: C-01 says 100 on *every* page, mobile and
    desktop. Publishing an average would let a failing page hide behind
    passing ones, which is precisely the kind of flattering summary the
    charter's honesty conditions exist to prevent.
    """
    runs = sorted(lhci_dir.glob("lhr-*.json"))
    if not runs:
        return {}

    worst: dict[str, float] = {}
    per_page: list[dict] = []
    raw: dict[tuple, dict[str, list]] = {}
    for f in runs:
        lhr = json.loads(f.read_text(encoding="utf-8"))
        url = lhr.get("finalDisplayedUrl") or lhr.get("finalUrl", "?")
        profile = lhr.get("configSettings", {}).get("formFactor", "?")
        row = {"url": url, "profile": profile}
        # THE PROTOCOL (director's ruling, 2026-08-06): median of 3 runs per
        # page per profile. Single-run figures are retired as non-evidence —
        # two consecutive CI runs of the same site gave 98 and 59, a 39-point
        # swing, so a single run measures the runner's mood, not the site.
        # The median is taken per (page, profile, category), then the WORST
        # median across pages and profiles is published, because C-01 asks for
        # every page on both profiles rather than a flattering average.
        bucket = raw.setdefault((url, profile), {})
        for key in ("performance", "accessibility", "best-practices", "seo"):
            cat = lhr.get("categories", {}).get(key)
            if cat is None or cat.get("score") is None:
                continue
            score = round(cat["score"] * 100)
            row[key] = score
            bucket.setdefault(key, []).append(score)
        audits = lhr.get("audits", {})
        for metric, aid in (("lcp_ms", "largest-contentful-paint"),
                            ("cls", "cumulative-layout-shift"),
                            ("tbt_ms", "total-blocking-time"),
                            ("transfer_bytes", "total-byte-weight")):
            a = audits.get(aid, {})
            if a.get("numericValue") is not None:
                row[metric] = a["numericValue"]

        # WHY a category missed, not just that it did. A published "92" that
        # does not say what cost the 8 points is a number nobody can act on,
        # and /audit exists to be actionable rather than decorative.
        failed = []
        for key, cat in lhr.get("categories", {}).items():
            if cat.get("score") is None or cat["score"] >= 1:
                continue
            for ref in cat.get("auditRefs", []):
                a = audits.get(ref.get("id"), {})
                if a.get("score") is not None and a["score"] < 1 and \
                        a.get("scoreDisplayMode") not in ("notApplicable", "informative"):
                    entry = {"category": key, "id": ref["id"],
                             "title": a.get("title", ""),
                             "score": a["score"]}
                    # The audit's own detail rows say WHICH rule failed and
                    # where. Without them a failing audit id is still a guess.
                    # details.items is USUALLY a list, but not always — some
                    # audits carry a dict there, and slicing it raised
                    # KeyError: slice(None, 5, None). Type-check rather than
                    # assume the shape of another tool's output.
                    details = a.get("details")
                    items = details.get("items") if isinstance(details, dict) else None
                    if isinstance(items, list) and items:
                        entry["items"] = items[:5]
                    elif items:
                        entry["items"] = [items]
                    if a.get("explanation"):
                        entry["explanation"] = a["explanation"]
                    failed.append(entry)
        if failed:
            row["failed_audits"] = failed
        per_page.append(row)

    # Median per (page, profile, category); then the worst median published.
    import statistics
    medians = []
    for (url, profile), cats in sorted(raw.items()):
        row = {"url": url, "profile": profile, "samples": {}}
        for key, scores in cats.items():
            med = round(statistics.median(scores))
            row["samples"][key] = {"runs": scores, "median": med}
            worst[key] = min(worst.get(key, 101), med)
        medians.append(row)

    samples_per_cell = sorted({len(s) for r in medians for s in
                               (v["runs"] for v in r["samples"].values())})
    return {"worst": worst, "runs": per_page, "run_count": len(runs),
            "medians": medians, "samples_per_cell": samples_per_cell,
            "protocol": ("median of 3 runs per page per profile, mobile and "
                         "desktop, against the published origin; the WORST "
                         "median across all pages and profiles is published")}


def is_home(run: dict) -> bool:
    """True for the home page only. Matched on the URL PATH, because every page
    on this site ends in a slash and `endswith('/')` therefore matches all of
    them (defect D-52)."""
    return urllib.parse.urlparse(run.get("url", "")).path in ("", "/")


def worst_median(runs: list[dict], metric: str, only=None) -> float | None:
    """The protocol, applied: median per (page, profile), then the WORST of
    those medians across every cell.

    The worst median, never the worst run. A single run measures the CI
    runner's mood — two consecutive runs of this same site once differed by 39
    Lighthouse points — which is why the protocol exists. Taking max() over
    individual runs re-imports exactly the noise the median removes, and is
    what defect D-52 was.
    """
    cells: dict[tuple, list[float]] = {}
    for r in runs:
        if metric not in r or (only is not None and not only(r)):
            continue
        cells.setdefault((r.get("url"), r.get("profile")), []).append(r[metric])
    if not cells:
        return None
    return max(statistics.median(v) for v in cells.values())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lighthouse", type=pathlib.Path)
    ap.add_argument("--vnu", type=pathlib.Path)
    ap.add_argument("--axe", type=pathlib.Path)
    ap.add_argument("--gates", type=pathlib.Path,
                    help="tools/gate_status.py output — the A2 charter-check "
                         "verdicts (defect D-48)")
    ap.add_argument("--measured-against", default="CI test server "
                    "(python http.server: no gzip, no cache headers)",
                    help="the environment these figures describe")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    measured: dict[str, str] = {}
    detail: dict[str, object] = {}

    # --- Lighthouse -------------------------------------------------------
    lh = lighthouse_scores(args.lighthouse) if args.lighthouse else {}
    if lh.get("worst"):
        w = lh["worst"]
        measured["lighthouse"] = (f"{w.get('performance','?')} / "
                                  f"{w.get('accessibility','?')} / "
                                  f"{w.get('best-practices','?')} / "
                                  f"{w.get('seo','?')}")
        detail["lighthouse"] = lh
        # DEFECT D-52. These three metrics did NOT follow the median-of-3
        # protocol printed beside them on /audit. LCP and CLS took max() over
        # every individual run — the worst SINGLE run — and transfer took an
        # arbitrary one. Only the category scores above ever implemented the
        # protocol.
        #
        # The cost was not theoretical: the published LCP swung 1.65 -> 2.25 ->
        # 2.28 -> 2.32 s across four measurements while the worst MEDIAN sat
        # still at 1.53-1.56 s. That swing is precisely the single-run noise the
        # protocol was adopted to eliminate, and it nearly triggered a revert of
        # work whose true cost was 0.02 s.
        #
        # Corrected to the pre-registered method: median per (page, profile),
        # then the WORST median across all cells. The protocol was printed
        # before any result existed and the scores already implemented it, so
        # this is the code being brought to its own pre-registration — not a
        # figure being chosen. Rewriting the printed protocol to match the bug
        # is what would have been result-shopping.
        worst_lcp = worst_median(lh["runs"], "lcp_ms")
        worst_cls = worst_median(lh["runs"], "cls")
        if worst_lcp is not None:
            measured["lcp"] = f"{worst_lcp/1000:.2f} s (worst median)"
        if worst_cls is not None:
            measured["cls"] = f"{worst_cls:.3f} (worst median)"

        # A1.5 is "Home first-view transfer", so it is the home page only. The
        # old filter was `url.endswith("/")`, which matches EVERY page on this
        # site — /projects/, /audit/ and the rest all end in a slash — so the
        # figure was the first run of whatever sorted first, not the home page
        # by construction. Matched on the URL PATH instead.
        home_transfer = worst_median(lh["runs"], "transfer_bytes", is_home)
        if home_transfer is not None:
            measured["transfer"] = f"{int(round(home_transfer)):,} B"

    # --- axe --------------------------------------------------------------
    if args.axe and args.axe.exists():
        axe = json.loads(args.axe.read_text(encoding="utf-8"))
        measured["axe"] = f"{axe['total_violations']} violations"
        detail["axe"] = axe

    # --- W3C Nu validator -------------------------------------------------
    if args.vnu and args.vnu.exists():
        vnu = json.loads(args.vnu.read_text(encoding="utf-8"))
        errors = [m for m in vnu.get("messages", []) if m.get("type") == "error"]
        measured["validator"] = f"{len(errors)} errors"
        detail["validator"] = {"errors": len(errors),
                               "sample": [m.get("message") for m in errors[:5]]}

    # --- contrast (deterministic; same everywhere) ------------------------
    # DEFECT D-55. This ran check_contrast.py, DISCARDED its output entirely,
    # and on exit 0 wrote a hard-coded string with the figure "5.78:1" typed by
    # hand. The checker's own numbers never reached the page. If a token had
    # changed, the gate would still have exited 0 and /audit would have gone on
    # publishing 5.78 — a figure with no producer behind it, which is exactly
    # D-52's family, and on the one page whose subject is its own accuracy.
    #
    # The summary is now DERIVED, and the per-token rows for both themes are
    # carried into detail so /audit can publish the table rather than a
    # sentence about it.
    with tempfile.TemporaryDirectory() as td:
        contrast_json = pathlib.Path(td) / "contrast.json"
        r = subprocess.run(
            [sys.executable, "tools/check_contrast.py", "--json-out", str(contrast_json)],
            cwd=ROOT, capture_output=True, text=True)
        if r.returncode == 0 and contrast_json.exists():
            doc = json.loads(contrast_json.read_text(encoding="utf-8"))
            measured["contrast"] = doc["summary"]
            detail["contrast"] = doc

    # --- charter-check gates (defect D-48) --------------------------------
    # These are NOT measurements of the published origin. They are the exit
    # codes of the gates run against the checked-out commit, recorded with the
    # SHA they ran against so the page can say which tree they describe. Absent
    # here means absent on the page: a row with no producer renders its
    # declared basis, never a verification mark.
    gates: dict = {}
    if args.gates and args.gates.exists():
        gates = json.loads(args.gates.read_text(encoding="utf-8"))

    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "_generated": ("Machine-written by tools/write_audit.py in CI from tool "
                       "output. NEVER hand-edited. A value with no measurement "
                       "is ABSENT, so /audit renders '— AT DEPLOY' rather than a "
                       "plausible-looking number."),
        "as_of": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "as_of_display": now.astimezone(
            dt.timezone(dt.timedelta(hours=5, minutes=30))).strftime("%Y-%m-%d %H:%M IST"),
        "measured": measured,
        # WHICH environment produced these figures. Without it a
        # performance number is unreadable: the CI test server sends no
        # gzip and no cache headers, the published origin sends both.
        "measured_against": args.measured_against,
        "detail": detail,
        "gates": gates,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                   encoding="utf-8", newline="\n")

    print(f"wrote {OUT.relative_to(ROOT)}  as of {payload['as_of_display']}")
    if not measured:
        print("  NO MEASURED VALUES — every /audit cell will read '— AT DEPLOY'")
    if lh:
        profiles = sorted({r["profile"] for r in lh.get("runs", [])})
        print(f"  runs         {lh.get('run_count', 0)} lighthouse reports "
              f"across profiles: {', '.join(profiles) or 'none'}")
        if len(profiles) < 2:
            print("  WARNING  fewer than two form factors measured — C-01 "
                  "requires mobile AND desktop (defect D-41)")
    for k, v in sorted(measured.items()):
        print(f"  {k:<12} {v}")

    # Print every audit that cost points, so a missed condition is diagnosable
    # from the CI log rather than requiring a re-run to investigate.
    seen = set()
    for row in lh.get("runs", []):
        for f in row.get("failed_audits", []):
            key = (f["category"], f["id"])
            if key in seen:
                continue
            seen.add(key)
            print(f"  WHY {f['category']:<16} {f['id']:<34} {f['title'][:60]}")
            if f.get("explanation"):
                print(f"      explanation: {f['explanation'][:200]}")
            for item in f.get("items", []):
                print(f"      item: {json.dumps(item)[:220]}")
    for key, res in sorted(gates.get("results", {}).items()):
        print(f"  gate {key:<16} {res['status']:<4} {res['detail']}")
    if gates.get("commit"):
        print(f"  gates ran against commit {gates['commit'][:7]}")

    absent = {"lighthouse", "axe", "validator", "contrast"} - set(measured)
    if absent:
        print(f"  absent (renders '— AT DEPLOY'): {', '.join(sorted(absent))}")
    return 0


def selftest() -> int:
    """Prove the tool refuses to invent a score."""
    import tempfile
    ok = True
    print("SELFTEST — a missing tool output must produce ABSENCE, not a number\n")

    with tempfile.TemporaryDirectory() as td:
        empty = pathlib.Path(td)
        # No lhr-*.json at all.
        result = lighthouse_scores(empty)
        good = result == {}
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] no Lighthouse output -> no scores "
              f"(got {result or 'nothing'})")

        # A report whose category score is null must not become 0 or 100.
        (empty / "lhr-1.json").write_text(json.dumps({
            "finalDisplayedUrl": "http://x/", "configSettings": {"formFactor": "mobile"},
            "categories": {"performance": {"score": None},
                           "seo": {"score": 1.0}}}), encoding="utf-8")
        result = lighthouse_scores(empty)
        w = result.get("worst", {})
        good = "performance" not in w and w.get("seo") == 100
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] a null category is omitted, not "
              f"defaulted (worst={w})")

        # The worst score wins, never the average.
        (empty / "lhr-2.json").write_text(json.dumps({
            "finalDisplayedUrl": "http://y/", "configSettings": {"formFactor": "desktop"},
            "categories": {"seo": {"score": 0.62}}}), encoding="utf-8")
        w = lighthouse_scores(empty).get("worst", {})
        good = w.get("seo") == 62
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] the WORST page wins, not the average "
              f"(seo={w.get('seo')}, pages were 100 and 62)")

        # The protocol's own control: three runs of one page must publish the
        # MEDIAN, not the best and not the worst sample.
        for f in empty.glob("lhr-*.json"):
            f.unlink()
        for i, score in enumerate((0.59, 0.98, 0.83)):
            (empty / f"lhr-{i}.json").write_text(json.dumps({
                "finalDisplayedUrl": "http://z/",
                "configSettings": {"formFactor": "mobile"},
                "categories": {"performance": {"score": score}}}), encoding="utf-8")
        w = lighthouse_scores(empty).get("worst", {})
        good = w.get("performance") == 83
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] median of 3 published, not best "
              f"or worst (runs 59/98/83 -> {w.get('performance')}, expect 83)")

    # --- D-52 controls: the SAME protocol, for the metrics that never had it --
    # These are the real numbers from the 2026-08-10 measurement. The old code
    # published 2.32 (the worst single run) and nearly triggered a revert; the
    # protocol's answer is 1.56, and the difference between those two is the
    # whole defect.
    runs = [
        {"url": "https://x/", "profile": "mobile", "lcp_ms": 1530, "cls": 0.0,
         "transfer_bytes": 143354},
        {"url": "https://x/", "profile": "mobile", "lcp_ms": 1560, "cls": 0.0,
         "transfer_bytes": 143358},
        {"url": "https://x/", "profile": "mobile", "lcp_ms": 2320, "cls": 0.0,
         "transfer_bytes": 143377},
        {"url": "https://x/projects/", "profile": "mobile", "lcp_ms": 1280},
        {"url": "https://x/projects/", "profile": "mobile", "lcp_ms": 1500},
        {"url": "https://x/projects/", "profile": "mobile", "lcp_ms": 1610},
    ]
    checks = [
        ("LCP publishes the worst MEDIAN, not the worst run",
         worst_median(runs, "lcp_ms"), 1560),
        ("an outlier run cannot move the published figure",
         worst_median(runs[:3], "lcp_ms"), 1560),
        ("transfer is the HOME page only, matched on path not a trailing slash",
         worst_median(runs, "transfer_bytes", is_home), 143358),
        ("a metric no run carries is ABSENT, never zero",
         worst_median(runs, "tbt_ms"), None),
    ]
    for label, got, expect in checks:
        good = got == expect
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label} (got {got}, expect {expect})")

    good = is_home({"url": "https://x/"}) and not is_home({"url": "https://x/audit/"})
    ok = ok and good
    print(f"  [{'PASS' if good else 'FAIL'}] '/audit/' is not the home page — the "
          f"old endswith('/') filter matched every page on the site")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
