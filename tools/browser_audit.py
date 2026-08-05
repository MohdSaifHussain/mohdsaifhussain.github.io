"""Real-browser audit: CSP violations and axe-core.  P3.4 / D2.

Discharges obligation O-10, which exists because P3.2 verified JSON-LD's CSP
safety against the WHATWG HTML specification. That reading was correct and it
was NOT execution (doctrine rule 4). This runs a browser and reads what it says.

WHERE THIS RUNS, and why. Director's standing principle, adopted P3.2:
    "local success is not evidence about CI; any figure destined for /audit is
     measured in the environment that publishes it."
So this runs in CI only, against the built _site served locally, BEFORE deploy —
so an axe violation or a CSP error blocks publication rather than being
discovered afterwards. The builder has no local browser, deliberately: a figure
measured here would be exactly what that principle says is not evidence.

WHAT COUNTS AS A FAILURE
  - any axe-core violation                       -> AXE_VIOLATION   (C-06)
  - any CSP violation reported by the browser    -> CSP_VIOLATION   (C-18)
  - any console error or uncaught page error     -> CONSOLE_ERROR
A clean run prints what it examined, never a bare pass (doctrine).

Usage (CI):
    python tools/browser_audit.py --root _site
"""

from __future__ import annotations

import argparse
import functools
import http.server
import json
import pathlib
import socketserver
import sys
import threading

sys.stdout.reconfigure(encoding="utf-8")     # defect D-13
sys.stderr.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
AXE = ROOT / "node_modules" / "axe-core" / "axe.min.js"

PAGES = ["/", "/projects/", "/experience/", "/certifications/", "/audit/"]


def serve(directory: pathlib.Path, port: int) -> socketserver.TCPServer:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=str(directory))
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def audit(base: str) -> tuple[list[tuple[str, str]], dict]:
    from playwright.sync_api import sync_playwright

    if not AXE.exists():
        sys.exit(f"REASON=AXE_MISSING  {AXE} not found (run: npm ci)")
    axe_source = AXE.read_text(encoding="utf-8")

    problems: list[tuple[str, str]] = []
    summary: dict[str, dict] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for path in PAGES:
            page = browser.new_page()
            console_errors: list[str] = []
            csp_violations: list[str] = []

            page.on("console", lambda msg: (
                console_errors.append(msg.text) if msg.type == "error" else None))
            page.on("pageerror", lambda err: console_errors.append(f"pageerror: {err}"))

            # The browser's own CSP reporting, not an inference from console text.
            page.add_init_script("""
                window.__cspViolations = [];
                document.addEventListener('securitypolicyviolation', function (e) {
                    window.__cspViolations.push(
                        e.violatedDirective + ' blocked ' + (e.blockedURI || '(inline)'));
                });
            """)

            page.goto(base + path, wait_until="networkidle")
            csp_violations = page.evaluate("window.__cspViolations || []")

            page.evaluate(axe_source)
            result = page.evaluate("() => axe.run(document, {resultTypes: ['violations']})")
            violations = result.get("violations", [])

            summary[path] = {
                "axe_violations": len(violations),
                "axe_passes_checked": len(result.get("passes", [])),
                "csp_violations": len(csp_violations),
                "console_errors": len(console_errors),
            }

            for v in violations:
                nodes = "; ".join(n.get("target", [""])[0] for n in v.get("nodes", [])[:3])
                problems.append(("AXE_VIOLATION",
                                 f"{path}  [{v['impact']}] {v['id']}: {v['help']}  -> {nodes}"))
            for c in csp_violations:
                problems.append(("CSP_VIOLATION", f"{path}  {c}"))
            for e in console_errors:
                problems.append(("CONSOLE_ERROR", f"{path}  {e[:200]}"))

            page.close()
        browser.close()

    return problems, summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="_site")
    ap.add_argument("--port", type=int, default=8765)
    args = ap.parse_args()

    root = (ROOT / args.root).resolve()
    if not root.is_dir():
        sys.exit(f"REASON=SITE_MISSING  {root}")

    httpd = serve(root, args.port)
    try:
        problems, summary = audit(f"http://127.0.0.1:{args.port}")
    finally:
        httpd.shutdown()

    print("Browser audit — what was examined:\n")
    print(f"  {'page':<20}{'axe violations':>16}{'CSP violations':>16}{'console errors':>16}")
    for path, s in summary.items():
        print(f"  {path:<20}{s['axe_violations']:>16}{s['csp_violations']:>16}"
              f"{s['console_errors']:>16}")

    print(f"\n  pages loaded          : {len(summary)}")
    print(f"  axe-core rules run    : the full default ruleset, per page")
    print(f"  CSP violations counted: from the browser's securitypolicyviolation "
          f"event, not inferred from console text")

    if problems:
        print("\nBROWSER AUDIT FAILED")
        for reason, detail in problems:
            print(f"  REASON={reason}  {detail}")
        return 1

    print("\nBROWSER AUDIT OK — zero axe violations, zero CSP violations, "
          "zero console errors, across every page")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
