"""C-12 / C-15: what actually moves must match what is declared.  P3.3 / D7.

Handoff §5 originally called its list complete at three. It is now four, by the
director's recorded ruling adding A3.4. The guarantee was restated rather than
abandoned:

    "Nothing else ships" is preserved as:
    THE LIST CHANGES ONLY BY RECORDED RULING, NEVER SILENTLY.

That is a stronger guarantee than a frozen number. A frozen count can only be
honoured by refusing good changes or by breaking it quietly. A declared list
can absorb a genuine improvement while an UNDECLARED animation stays a defect.

So this checks BOTH directions against data/audit-spec.json:
  - motion that ships but is not declared  -> UNDECLARED_ANIMATION
  - motion declared but not shipped        -> UNSHIPPED_ANIMATION
and separately enforces C-15's property and duration rules:
  - anything but transform/opacity animated -> FORBIDDEN_PROPERTY
  - a transition longer than 400ms          -> DURATION_EXCEEDED

C-10 AND C-14 ADDED HERE (defect D-48). Until D-48 these two conditions had NO
automated producer anywhere in the repository, while /audit carried rows for
both (A2.2, A2.7) promising a value "measured by CI at publish time". They are
motion and scrolling conditions, so they belong in the motion checker rather
than in a new tool:
  - a transition that cannot be neutralised
    under prefers-reduced-motion             -> MOTION_NOT_REDUCED   (C-10)
  - scroll-behavior: smooth, a hidden
    scrollbar on a snap container, or JS
    that drives scrolling                    -> SCROLL_NOT_NATIVE    (C-14)

Only the MECHANICAL half of C-10 is checkable here: that the motion can be
switched off. Whether the page remains COHERENT with it switched off is a human
observation, recorded and dated in docs/INTERACTION-QA.md, and /audit links that
rather than claiming a machine measured it.

Usage (PowerShell):
    python tools\\check_animations.py
    python tools\\check_animations.py --selftest
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")     # defect D-13
sys.stderr.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS = ROOT / "static" / "css"
JS = ROOT / "static" / "js"
SPEC = ROOT / "data" / "audit-spec.json"

# C-15: compositor-friendly only. `background-color` and `color` are permitted
# ONLY as instant state changes with no transition — that is what makes A3.3
# and A3.4 "0ms" rather than animations of a non-compositor property.
ANIMATABLE = {"transform", "opacity"}
FORBIDDEN = {"width", "height", "top", "left", "right", "bottom", "margin", "padding"}
MAX_TRANSITION_MS = 400

TRANSITION = re.compile(r"transition:\s*([^;}]+)", re.I)
ANIMATION = re.compile(r"animation(?:-name)?:\s*([^;}]+)", re.I)
KEYFRAMES = re.compile(r"@keyframes\s+([\w-]+)", re.I)
DURATION = re.compile(r"([\d.]+)\s*(ms|s)\b", re.I)
CUSTOM_PROP = re.compile(r"var\(\s*(--[\w-]+)", re.I)

# C-10. The media query is the only switch the platform gives us, so it must
# exist and it must actually zero the durations the transitions read.
# Ref: CSS Media Queries Level 5, prefers-reduced-motion.
REDUCED_MOTION_AT = re.compile(r"@media[^{]*prefers-reduced-motion[^{]*\{", re.I)

# C-14. Scrolling stays the browser's, and the position stays visible.
SCROLL_BEHAVIOR = re.compile(r"scroll-behavior:\s*smooth", re.I)
SCROLLBAR_HIDDEN = re.compile(
    r"scrollbar-width:\s*none|::-webkit-scrollbar\s*\{[^}]*display:\s*none", re.I)
# Scripted scrolling. `scroll-behavior: smooth` is CSS-side; these are JS-side.
# Ref: CSSOM View — scrollTo/scrollBy/scrollIntoView all move the viewport
# programmatically, which is exactly what "native scrolling only" excludes.
JS_SCROLL_DRIVE = re.compile(
    r"\.(scrollTo|scrollBy|scrollIntoView)\s*\(|"
    r"scrollTop\s*=|scrollLeft\s*=", re.I)
JS_SCROLL_SUPPRESS = re.compile(
    r"addEventListener\(\s*[\"'](wheel|touchmove|scroll)[\"']", re.I)


def css_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(CSS.glob("*.css")))


def js_text() -> str:
    if not JS.is_dir():
        return ""
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(JS.glob("*.js")))


def _block_after(text: str, open_brace_end: int) -> str:
    """The body of the brace-delimited block whose '{' ends at open_brace_end.

    Written as a brace counter rather than a regex because @media bodies nest
    one level (`@media { :root { ... } }`) and a non-greedy regex stops at the
    first inner '}', silently reading an empty block — which would make this
    check pass by accident. A check that can pass by accident is D-44.
    """
    depth, i = 1, open_brace_end
    while i < len(text) and depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[open_brace_end:i - 1]


def reduced_motion_body(css: str) -> str | None:
    m = REDUCED_MOTION_AT.search(css)
    return None if m is None else _block_after(css, m.end())


def check_reduced_motion(css: str) -> list[tuple[str, str]]:
    """C-10: every timed transition must be switchable off.

    A transition is considered neutralised if either it has no non-zero
    duration at all (A3.3 and A3.4 are instant by design), or one of the custom
    properties it reads is set to zero inside the prefers-reduced-motion block.

    The "one of" is deliberate: `transition: opacity var(--motion-reveal)
    var(--ease-reveal)` reads two custom properties and only one of them is a
    duration. Requiring BOTH to be zeroed would demand that an easing curve be
    set to 0ms, which is meaningless. Requiring at least one is the honest
    guarantee available from the shorthand without resolving the cascade.
    """
    timed = []
    for m in TRANSITION.finditer(css):
        decl = m.group(1).strip()
        literal = [ms(v, u) for v, u in DURATION.findall(decl)]
        tokens = CUSTOM_PROP.findall(decl)
        if any(d > 0 for d in literal) or tokens:
            timed.append((decl, tokens))
    if not timed:
        return []

    body = reduced_motion_body(css)
    if body is None:
        return [("MOTION_NOT_REDUCED",
                 "timed motion ships but there is no @media "
                 "(prefers-reduced-motion: reduce) block at all (C-10)")]

    zeroed = {name for name, value in
              re.findall(r"(--[\w-]+)\s*:\s*([^;}]+)", body)
              if all(ms(v, u) == 0 for v, u in DURATION.findall(value))
              and DURATION.search(value)}

    problems = []
    for decl, tokens in timed:
        if tokens and not (set(tokens) & zeroed):
            problems.append((
                "MOTION_NOT_REDUCED",
                f"'{decl}' reads {', '.join(tokens)}, none of which is zeroed "
                f"under prefers-reduced-motion (C-10)"))
        elif not tokens:
            problems.append((
                "MOTION_NOT_REDUCED",
                f"'{decl}' hard-codes its duration, so reduced motion cannot "
                f"switch it off (C-10)"))
    return problems


def check_native_scroll(css: str, js: str) -> list[tuple[str, str]]:
    """C-14: the browser scrolls, and the scroll position stays visible."""
    problems = []
    if SCROLL_BEHAVIOR.search(css):
        problems.append(("SCROLL_NOT_NATIVE",
                         "scroll-behavior: smooth overrides the browser's own "
                         "scrolling and is motion not on the declared list (C-14)"))
    if SCROLLBAR_HIDDEN.search(css):
        problems.append(("SCROLL_NOT_NATIVE",
                         "the scrollbar is hidden; C-14 requires the slider's "
                         "position to remain visible"))
    if "scroll-snap-type" in css and "overflow-x: auto" not in css \
            and "overflow-x:auto" not in css:
        problems.append(("SCROLL_NOT_NATIVE",
                         "a scroll-snap container ships without overflow-x: auto, "
                         "so it is not a natively scrollable region (C-14)"))
    for pattern, label in ((JS_SCROLL_DRIVE, "drives scrolling programmatically"),
                           (JS_SCROLL_SUPPRESS, "listens on wheel/touchmove/scroll")):
        m = pattern.search(js)
        if m:
            problems.append(("SCROLL_NOT_NATIVE",
                             f"shipped JavaScript {label}: '{m.group(0)}' (C-14)"))
    return problems


def declared_ids() -> list[str]:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    return [row["id"] for row in spec["a3_animations"]]


def ms(value: str, unit: str) -> float:
    return float(value) * (1000 if unit.lower() == "s" else 1)


def check_transitions(css: str) -> list[tuple[str, str]]:
    """C-15: only transform/opacity may be transitioned, and never over 400ms."""
    problems = []
    for m in TRANSITION.finditer(css):
        decl = m.group(1).strip()
        prop = decl.split()[0].lower()

        if prop in FORBIDDEN:
            problems.append(("FORBIDDEN_PROPERTY",
                             f"transition on '{prop}' is not compositor-friendly (C-15): {decl}"))
        elif prop not in ANIMATABLE and prop != "all":
            # colour/background transitions are only acceptable at 0ms, i.e. no
            # transition at all — which is how A3.3 and A3.4 are specified.
            durations = [ms(v, u) for v, u in DURATION.findall(decl)]
            if any(d > 0 for d in durations):
                problems.append(("FORBIDDEN_PROPERTY",
                                 f"'{prop}' is transitioned over time; A3.3/A3.4 are instant: {decl}"))
        if prop == "all":
            problems.append(("FORBIDDEN_PROPERTY",
                             f"transition: all animates whatever changes, including layout: {decl}"))

        for value, unit in DURATION.findall(decl):
            if ms(value, unit) > MAX_TRANSITION_MS:
                problems.append(("DURATION_EXCEEDED",
                                 f"{value}{unit} exceeds the {MAX_TRANSITION_MS}ms ceiling (C-15): {decl}"))
    return problems


def check_keyframes(css: str) -> list[tuple[str, str]]:
    """Any @keyframes block is motion that must be declared and compositor-safe."""
    problems = []
    for m in KEYFRAMES.finditer(css):
        problems.append(("UNDECLARED_ANIMATION",
                         f"@keyframes {m.group(1)} — keyframe animation is not on the declared list"))
    return problems


def shipped_ids(css: str) -> set[str]:
    """Which declared animations are actually implemented.

    Each is identified by the marker comment its implementation carries, so a
    declaration cannot be satisfied by wishful thinking and an implementation
    cannot exist without naming which entry it is.
    """
    return set(re.findall(r"/\*+\s*(?:.*?\b)?(A3\.\d)\b", css)) | \
           set(re.findall(r"\b(A3\.\d)\b", css))


def check_list_agreement(css: str) -> list[tuple[str, str]]:
    declared, shipped = set(declared_ids()), shipped_ids(css)
    problems = []
    for extra in sorted(shipped - declared):
        problems.append(("UNDECLARED_ANIMATION",
                         f"{extra} is implemented in CSS but not declared in audit-spec.json"))
    for missing in sorted(declared - shipped):
        problems.append(("UNSHIPPED_ANIMATION",
                         f"{missing} is declared in audit-spec.json but not implemented in CSS"))
    return problems


def run() -> int:
    css, js = css_text(), js_text()
    problems = (check_transitions(css) + check_keyframes(css)
                + check_list_agreement(css)
                + check_reduced_motion(css) + check_native_scroll(css, js))

    declared = declared_ids()
    print(f"declared animations ({len(declared)}): {', '.join(declared)}")
    print(f"implemented in CSS  : {', '.join(sorted(shipped_ids(css))) or 'none found'}")
    body = reduced_motion_body(css)
    print(f"reduced-motion block: {'present' if body is not None else 'ABSENT'}"
          f"{'' if body is None else ' — ' + ' '.join(body.split())[:60]}")
    print(f"shipped JS scanned  : {len(list(JS.glob('*.js'))) if JS.is_dir() else 0} file(s) "
          f"for scroll interference (C-14)")

    if problems:
        print("\nANIMATION CHECK FAILED")
        for reason, detail in problems:
            print(f"  REASON={reason}  {detail}")
        return 1
    print("\nANIMATION OK — what ships matches what is declared, both directions;"
          "\n               motion is switchable off (C-10); scrolling is native (C-14)")
    return 0


def selftest() -> int:
    ok = True
    print("SELFTEST — both directions of the declared list, plus C-15 rules\n")
    cases = [
        ("a fourth, undeclared animation MUST trip",
         lambda: check_list_agreement("/* A3.9 rogue */ .x{opacity:0}"),
         "UNDECLARED_ANIMATION", True),
        ("@keyframes MUST trip",
         lambda: check_keyframes("@keyframes pulse { from {opacity:0} }"),
         "UNDECLARED_ANIMATION", True),
        ("a width transition MUST trip (C-15)",
         lambda: check_transitions(".x{transition: width 200ms ease}"),
         "FORBIDDEN_PROPERTY", True),
        ("transition: all MUST trip",
         lambda: check_transitions(".x{transition: all 200ms}"),
         "FORBIDDEN_PROPERTY", True),
        ("a timed colour transition MUST trip (A3.3/A3.4 are instant)",
         lambda: check_transitions(".x{transition: color 150ms ease}"),
         "FORBIDDEN_PROPERTY", True),
        ("a transition over 400ms MUST trip (C-15)",
         lambda: check_transitions(".x{transition: opacity 900ms ease}"),
         "DURATION_EXCEEDED", True),
        ("the real opacity transition MUST NOT trip",
         lambda: check_transitions(".x{transition: opacity 200ms ease}"),
         "FORBIDDEN_PROPERTY", False),
        ("a transform transition MUST NOT trip",
         lambda: check_transitions(".x{transition: transform 250ms ease}"),
         "FORBIDDEN_PROPERTY", False),

        # C-10, both directions (defect D-48).
        ("timed motion with NO reduced-motion block MUST trip (C-10)",
         lambda: check_reduced_motion(".x{transition: opacity var(--m) ease}"),
         "MOTION_NOT_REDUCED", True),
        ("a reduced-motion block that zeroes nothing MUST trip (C-10)",
         lambda: check_reduced_motion(
             ".x{transition: opacity var(--m) ease}"
             "@media (prefers-reduced-motion: reduce){:root{--other:0ms}}"),
         "MOTION_NOT_REDUCED", True),
        ("a hard-coded duration MUST trip — nothing can switch it off (C-10)",
         lambda: check_reduced_motion(
             ".x{transition: opacity 200ms ease}"
             "@media (prefers-reduced-motion: reduce){:root{--m:0ms}}"),
         "MOTION_NOT_REDUCED", True),
        ("the nested @media body MUST be read, not stopped at the inner brace",
         lambda: check_reduced_motion(
             ".x{transition: opacity var(--m) ease}"
             "@media (prefers-reduced-motion: reduce){:root{--m:0ms}}"),
         "MOTION_NOT_REDUCED", False),
        ("instant-only CSS MUST NOT trip — there is nothing to reduce",
         lambda: check_reduced_motion(".x{color:red}"),
         "MOTION_NOT_REDUCED", False),

        # C-14, both directions (defect D-48).
        ("scroll-behavior: smooth MUST trip (C-14)",
         lambda: check_native_scroll(".x{scroll-behavior: smooth}", ""),
         "SCROLL_NOT_NATIVE", True),
        ("a hidden scrollbar MUST trip (C-14)",
         lambda: check_native_scroll(".x{scrollbar-width: none}", ""),
         "SCROLL_NOT_NATIVE", True),
        ("scroll-snap without overflow-x: auto MUST trip (C-14)",
         lambda: check_native_scroll(".x{scroll-snap-type: x mandatory}", ""),
         "SCROLL_NOT_NATIVE", True),
        ("JS calling scrollIntoView MUST trip (C-14)",
         lambda: check_native_scroll("", "el.scrollIntoView({block:'start'})"),
         "SCROLL_NOT_NATIVE", True),
        ("JS listening on wheel MUST trip (C-14)",
         lambda: check_native_scroll("", "el.addEventListener('wheel', f)"),
         "SCROLL_NOT_NATIVE", True),
        ("the real slider shape MUST NOT trip (C-14)",
         lambda: check_native_scroll(
             ".slider{overflow-x: auto; scroll-snap-type: x mandatory}", ""),
         "SCROLL_NOT_NATIVE", False),
        ("the real clock JS MUST NOT trip (C-14)",
         lambda: check_native_scroll("", "var t=host.querySelector('[data-clock-text]')"),
         "SCROLL_NOT_NATIVE", False),
    ]
    for label, fn, reason, must_trip in cases:
        found = reason in [r for r, _ in fn()]
        good = found == must_trip
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] "
              f"{'refused' if found else 'accepted':<8} {label}")

    # Positive control at repo level.
    real = check_transitions(css_text()) + check_keyframes(css_text()) + \
        check_list_agreement(css_text()) + check_reduced_motion(css_text()) + \
        check_native_scroll(css_text(), js_text())
    if real:
        print(f"  [FAIL] real CSS unexpectedly refused: {real}")
        ok = False
    else:
        print("  [PASS] accepted real CSS: declared list and shipped motion agree")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    return selftest() if args.selftest else run()


if __name__ == "__main__":
    raise SystemExit(main())
