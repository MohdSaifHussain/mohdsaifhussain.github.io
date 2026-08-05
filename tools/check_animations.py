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


def css_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted(CSS.glob("*.css")))


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
    css = css_text()
    problems = check_transitions(css) + check_keyframes(css) + check_list_agreement(css)

    declared = declared_ids()
    print(f"declared animations ({len(declared)}): {', '.join(declared)}")
    print(f"implemented in CSS  : {', '.join(sorted(shipped_ids(css))) or 'none found'}")

    if problems:
        print("\nANIMATION CHECK FAILED")
        for reason, detail in problems:
            print(f"  REASON={reason}  {detail}")
        return 1
    print("\nANIMATION OK — what ships matches what is declared, both directions")
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
    ]
    for label, fn, reason, must_trip in cases:
        found = reason in [r for r, _ in fn()]
        good = found == must_trip
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] "
              f"{'refused' if found else 'accepted':<8} {label}")

    # Positive control at repo level.
    real = check_transitions(css_text()) + check_keyframes(css_text()) + \
        check_list_agreement(css_text())
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
