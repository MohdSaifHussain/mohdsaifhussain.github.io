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

# P4.2. Both themes, every page. axe's colour-contrast rule evaluates what is
# RENDERED, so a palette that only exists under a media query is a palette axe
# has never looked at — and light mode would have shipped with its contrast
# checked by nobody but a static calculator.
THEMES = ("dark", "light")


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
          for theme in THEMES:
            # emulate_media at page creation, so the FIRST paint is already in
            # the theme under test — not a dark page repainted light after axe
            # has begun looking at it.
            page = browser.new_page(color_scheme=theme)
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

            # THE WITNESS. Requirement (4): the job must exercise both themes,
            # not assume the second. A loop that says "light" proves nothing —
            # if emulation silently failed, every run would be dark and every
            # run would still pass. So each run records the background it
            # actually rendered, and a check below refuses if the two themes
            # produced the same one.
            background = page.evaluate(
                "() => getComputedStyle(document.body).backgroundColor")

            summary[f"{path} [{theme}]"] = {
                "theme": theme,
                "background": background,
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
                                 f"{path} [{theme}]  [{v['impact']}] {v['id']}: "
                                 f"{v['help']}  -> {nodes}"))
            for c in csp_violations:
                problems.append(("CSP_VIOLATION", f"{path} [{theme}]  {c}"))
            for e in console_errors:
                problems.append(("CONSOLE_ERROR", f"{path} [{theme}]  {e[:200]}"))

            page.close()
        browser.close()

    # Did the two themes actually render differently? If colour-scheme
    # emulation had no effect, every page would report one background and the
    # "light" half of this audit would be dark pages wearing a label.
    seen = {th: {s["background"] for s in summary.values() if s["theme"] == th}
            for th in THEMES}
    if len(THEMES) > 1 and seen["dark"] & seen["light"]:
        problems.append((
            "THEME_NOT_APPLIED",
            f"dark and light rendered the same background {seen['dark'] & seen['light']} — "
            f"colour-scheme emulation did not take, so the light-mode half of "
            f"this audit examined dark pages"))

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



# --- Above-fold protection (P4.1 / D5, ruling condition 4) -------------------
#
# A3.6 reveals the Experience register on scroll. Every scroll-driven reveal
# carries the same risk: an element that starts at its `from` state and never
# reaches its `to` state is content that is permanently invisible. Above the
# fold that is also an LCP regression, and C-02 has ZERO headroom at 1.65s.
#
# The spec argues this is safe — an element already visible at first paint is
# past its `entry` range, so fill-mode `both` holds the FINAL keyframe. That
# argument is correct and it is still an argument. The ruling requires proof,
# so this measures the rendered page instead: every element with a real box
# intersecting the first-paint viewport must be fully opaque, BEFORE any
# scrolling happens.
#
# Ref, checked 2026-08-10: animation-range / fill-mode semantics —
# https://developer.mozilla.org/en-US/docs/Web/CSS/animation-range

ABOVE_FOLD_JS = """() => {
  const vh = window.innerHeight, vw = window.innerWidth;
  const out = [];
  for (const el of document.querySelectorAll('main *')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;      // no box: not rendered
    if (r.top >= vh || r.bottom <= 0) continue;          // below or above fold
    if (r.left >= vw || r.right <= 0) continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none') continue;
    const op = parseFloat(cs.opacity);
    if (op < 0.99 || cs.visibility === 'hidden') {
      out.push({
        tag: el.tagName.toLowerCase(),
        cls: (el.className && el.className.toString().slice(0, 60)) || '',
        opacity: op, visibility: cs.visibility,
        top: Math.round(r.top)
      });
    }
  }
  return out;
}"""


def above_fold(base: str, path: str, viewports, poison_selector: str = ""):
    """Elements inside the first-paint viewport that render hidden.

    The poison is applied through the CSSOM rather than by injecting a <style>
    element. The site ships `style-src 'self'`, so an injected stylesheet would
    be BLOCKED by its own CSP — the poison would never apply, the check would
    correctly find nothing, and the control would report a failure that means
    "CSP works", not "the check is broken". Writing el.style from script is not
    restricted by CSP, so the poison lands and the control tests what it claims
    to test.
    """
    from playwright.sync_api import sync_playwright

    findings = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for label, w, h in viewports:
            page = browser.new_page(viewport={"width": w, "height": h})
            page.goto(base + path, wait_until="load")
            if poison_selector:
                applied = page.evaluate(
                    "sel => { const n = document.querySelectorAll(sel);"
                    " n.forEach(e => e.style.setProperty("
                    "'opacity', '0', 'important')); return n.length; }",
                    poison_selector)
                if not applied:
                    raise SystemExit(
                        f"REASON=POISON_INEFFECTIVE  '{poison_selector}' matched "
                        f"nothing on {path}; the control would have proved nothing")
            for hit in page.evaluate(ABOVE_FOLD_JS):
                findings.append((label, hit))
            page.close()
        browser.close()
    return findings


def run_above_fold(base: str, poison_selector: str = "") -> int:
    viewports = [("mobile", 375, 667), ("desktop", 1280, 800)]
    path = "/experience/"
    findings = above_fold(base, path, viewports, poison_selector)

    print(f"Above-fold protection — {path}, before any scrolling")
    for label, w, h in viewports:
        print(f"  viewport {label:<8} {w}x{h}")
    if findings:
        print("\nABOVE-FOLD CHECK FAILED")
        for label, hit in findings:
            print(f"  REASON=ABOVE_FOLD_HIDDEN  [{label}] <{hit['tag']} "
                  f"class=\"{hit['cls']}\"> opacity={hit['opacity']} "
                  f"visibility={hit['visibility']} top={hit['top']}px")
        return 1
    print("\nABOVE-FOLD OK — every element with a box inside the first-paint "
          "viewport renders fully opaque, on both viewports")
    return 0


def selftest_above_fold(base: str) -> int:
    """Prove the check can fail. D-44: a guard only ever seen to pass is a
    decoration. The poison is the exact defect being guarded against — an
    above-fold element left at a reveal's `from` state."""
    print("SELFTEST — the above-fold check must refuse a hidden above-fold "
          "element\n")
    poisoned = run_above_fold(base, ".xp-row")
    good = poisoned != 0
    print(f"\n  [{'PASS' if good else 'FAIL'}] poisoned page refused "
          f"(exit {poisoned}, expected non-zero)\n")
    clean = run_above_fold(base)
    good2 = clean == 0
    print(f"\n  [{'PASS' if good2 else 'FAIL'}] real page accepted "
          f"(exit {clean}, expected 0)")
    return 0 if (good and good2) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="_site")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--selftest", action="store_true",
                    help="prove axe and the CSP can both fail")
    ap.add_argument("--above-fold", action="store_true",
                    help="P4.1 D5: no element in the first-paint viewport of "
                         "/experience/ may render hidden (ruling condition 4)")
    ap.add_argument("--selftest-above-fold", action="store_true",
                    help="prove the above-fold check can refuse")
    ap.add_argument("--json-out", type=pathlib.Path,
                    help="write the axe result for tools/write_audit.py")
    args = ap.parse_args()

    root = (ROOT / args.root).resolve()
    if not root.is_dir():
        sys.exit(f"REASON=SITE_MISSING  {root}")

    httpd = serve(root, args.port)
    base = f"http://127.0.0.1:{args.port}"
    try:
        # P4.1 / D5. Checked before the axe paths: the above-fold check needs a
        # browser but not axe-core, and coupling it to axe would make a C-02
        # protection depend on a node_modules install it does not use.
        if args.selftest_above_fold:
            return selftest_above_fold(base)
        if args.above_fold:
            return run_above_fold(base)
        if args.selftest:
            print("SELFTEST — both detectors must be able to fail\n")
            return selftest(base)
        problems, summary = audit(base)
    finally:
        httpd.shutdown()
        httpd.server_close()      # release the socket, not just the loop (D-36)

    print("Browser audit — what was examined:\n")
    print(f"  {'page [theme]':<30}{'rendered bg':<22}{'axe viol.':>11}"
          f"{'checks eval.':>14}{'CSP viol.':>11}{'console err.':>14}")
    for path, s in summary.items():
        print(f"  {path:<30}{s.get('background', '?'):<22}{s['axe_violations']:>11}"
              f"{s['checks_evaluated']:>14}{s['csp_violations']:>11}"
              f"{s['console_errors']:>14}")

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

    themes_seen = sorted({s.get("theme") for s in summary.values() if s.get("theme")})
    backgrounds = sorted({s.get("background") for s in summary.values()})
    print(f"  themes exercised      : {', '.join(themes_seen) or 'none'}")
    print(f"  distinct backgrounds  : {', '.join(backgrounds)}  "
          f"(the witness that both themes actually rendered)")

    print("\nBROWSER AUDIT OK — zero axe violations, zero CSP violations, "
          "zero console errors,\n                   across every page IN EVERY "
          "THEME")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
