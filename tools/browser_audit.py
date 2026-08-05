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


class _Server(socketserver.TCPServer):
    # Defect D-36: shutdown() stops the serve_forever loop but does NOT close
    # the listening socket. The selftest step left the port bound, and the real
    # audit step then died with "Address already in use" — a green selftest
    # followed by a crash that had nothing to do with the site.
    allow_reuse_address = True


def serve(directory: pathlib.Path, port: int) -> _Server:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler,
                                directory=str(directory))
    httpd = _Server(("127.0.0.1", port), handler)
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
            rules_available = page.evaluate("() => axe.getRules().length")
            result = page.evaluate("() => axe.run(document)")
            violations = result.get("violations", [])

            summary[path] = {
                "axe_violations": len(violations),
                "rules_available": rules_available,
                # Evidence that axe actually EVALUATED this page. Without it,
                # "0 violations" is indistinguishable from "axe never ran".
                "checks_evaluated": len(violations) + len(result.get("passes", []))
                + len(result.get("incomplete", [])) + len(result.get("inapplicable", [])),
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


def selftest(base: str) -> int:
    """Prove BOTH detectors can fail, on the real deployed markup.

    Doctrine rule 5: a check that has only ever passed is a decoration. A
    zero-violation browser audit is exactly the result that deserves the most
    suspicion, because "axe found nothing" and "axe never ran" print the same.

    Both controls poison a REAL page in the browser rather than a fixture, so
    they exercise the same code path the real audit uses.
    """
    from playwright.sync_api import sync_playwright

    axe_source = AXE.read_text(encoding="utf-8")
    ok = True

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # --- Negative control 1: axe must catch an accessibility defect ------
        page = browser.new_page()
        page.goto(base + "/", wait_until="networkidle")
        page.evaluate("""() => {
            const img = document.createElement('img');
            img.src = '/assets/img/icon-192.png';   /* same-origin, CSP-allowed */
            document.body.appendChild(img);          /* deliberately no alt */
        }""")
        page.evaluate(axe_source)
        result = page.evaluate("() => axe.run(document)")
        ids = [v["id"] for v in result.get("violations", [])]
        caught = "image-alt" in ids
        ok = ok and caught
        print(f"  [{'PASS' if caught else 'FAIL'}] axe detects an image with no alt "
              f"-> violations: {ids or 'none'}")
        page.close()

        # --- Negative control 2: the CSP must block an inline script ---------
        page = browser.new_page()
        page.add_init_script("""
            window.__cspViolations = [];
            document.addEventListener('securitypolicyviolation', function (e) {
                window.__cspViolations.push(e.violatedDirective);
            });
        """)
        page.goto(base + "/", wait_until="networkidle")
        # Appended as a DOM element, so the CSP applies. page.evaluate() itself
        # runs via the debugger protocol and is NOT subject to the page policy —
        # using it to "test" the CSP would prove nothing.
        page.evaluate("""() => {
            const s = document.createElement('script');
            s.textContent = 'window.__pwned = true;';
            document.body.appendChild(s);
        }""")
        page.wait_for_timeout(200)
        violations = page.evaluate("window.__cspViolations || []")
        pwned = page.evaluate("window.__pwned === true")
        blocked = bool(violations) and not pwned
        ok = ok and blocked
        print(f"  [{'PASS' if blocked else 'FAIL'}] CSP blocks an injected inline script "
              f"-> {violations or 'NO VIOLATION REPORTED'}; executed={pwned}")
        page.close()

        browser.close()

    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="_site")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--selftest", action="store_true",
                    help="prove axe and the CSP can both fail")
    ap.add_argument("--json-out", type=pathlib.Path,
                    help="write the axe result for tools/write_audit.py")
    args = ap.parse_args()

    root = (ROOT / args.root).resolve()
    if not root.is_dir():
        sys.exit(f"REASON=SITE_MISSING  {root}")

    httpd = serve(root, args.port)
    base = f"http://127.0.0.1:{args.port}"
    try:
        if args.selftest:
            print("SELFTEST — both detectors must be able to fail\n")
            return selftest(base)
        problems, summary = audit(base)
    finally:
        httpd.shutdown()
        httpd.server_close()      # release the socket, not just the loop (D-36)

    print("Browser audit — what was examined:\n")
    print(f"  {'page':<20}{'axe viol.':>11}{'checks eval.':>14}"
          f"{'CSP viol.':>11}{'console err.':>14}")
    for path, s in summary.items():
        print(f"  {path:<20}{s['axe_violations']:>11}{s['checks_evaluated']:>14}"
              f"{s['csp_violations']:>11}{s['console_errors']:>14}")

    rules = next(iter(summary.values()))["rules_available"] if summary else 0
    if args.json_out:
        args.json_out.write_text(json.dumps({
            "total_violations": sum(s["axe_violations"] for s in summary.values()),
            "total_checks_evaluated": sum(s["checks_evaluated"] for s in summary.values()),
            "rules_loaded": next(iter(summary.values()))["rules_available"] if summary else 0,
            "pages": summary,
        }, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
        print(f"  axe result written to : {args.json_out}")

    print(f"\n  pages loaded          : {len(summary)}")
    print(f"  axe-core rules loaded : {rules}")
    print(f"  CSP violations counted: from the browser's securitypolicyviolation "
          f"event, not inferred from console text")
    print(f"  checks evaluated      : reported per page above, so a zero-violation "
          f"result is distinguishable from axe never having run")

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
