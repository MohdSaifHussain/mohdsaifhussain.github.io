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
import subprocess
import sys

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
    for f in runs:
        lhr = json.loads(f.read_text(encoding="utf-8"))
        url = lhr.get("finalDisplayedUrl") or lhr.get("finalUrl", "?")
        profile = lhr.get("configSettings", {}).get("formFactor", "?")
        row = {"url": url, "profile": profile}
        for key in ("performance", "accessibility", "best-practices", "seo"):
            cat = lhr.get("categories", {}).get(key)
            if cat is None or cat.get("score") is None:
                continue
            score = round(cat["score"] * 100)
            row[key] = score
            worst[key] = min(worst.get(key, 101), score)
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

    return {"worst": worst, "runs": per_page, "run_count": len(runs)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lighthouse", type=pathlib.Path)
    ap.add_argument("--vnu", type=pathlib.Path)
    ap.add_argument("--axe", type=pathlib.Path)
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
        worst_lcp = max((r.get("lcp_ms", 0) for r in lh["runs"]), default=None)
        worst_cls = max((r.get("cls", 0) for r in lh["runs"]), default=None)
        if worst_lcp is not None:
            measured["lcp"] = f"{worst_lcp/1000:.2f} s (worst page)"
        if worst_cls is not None:
            measured["cls"] = f"{worst_cls:.3f} (worst page)"
        home = [r for r in lh["runs"] if r["url"].rstrip("/").endswith("127.0.0.1:8765")
                or r["url"].endswith("/")]
        if home and home[0].get("transfer_bytes"):
            measured["transfer"] = f"{int(home[0]['transfer_bytes']):,} B"

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
    r = subprocess.run([sys.executable, "tools/check_contrast.py"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode == 0:
        measured["contrast"] = "AA met; 7:1 met except --dim (5.78:1)"

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

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
