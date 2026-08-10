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
# D-49: an explicit implementation marker. Deliberately not a bare `A3.N`,
# which occurs throughout ordinary comment prose in both stylesheets.
SHIPS = re.compile(r"@ships\s+(A3\.\d)", re.I)
DECLARATION = re.compile(r"([-\w]+)\s*:\s*[^;{}]+", re.I)
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


def _strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", " ", css, flags=re.S)


def _without_keyframes(css: str) -> str:
    """Keyframe BODIES are not rules that can be neutralised; the animation
    declarations that reference them are. Removing the bodies keeps `from`/`to`
    out of the selector scan below."""
    out, i = [], 0
    for m in KEYFRAMES.finditer(css):
        brace = css.find("{", m.end())
        if brace == -1:
            continue
        out.append(css[i:m.start()])
        i = brace + len(_block_after(css, brace + 1)) + 2
    out.append(css[i:])
    return "".join(out)


def _innermost_rules(css: str) -> list[tuple[str, str]]:
    """(selector prelude, declaration body) for every rule with no nested rule.

    Innermost only, which is what makes this work through `@supports` and
    `@media` wrappers without parsing them: the wrapper's prelude contains no
    braces, so the match starts after its opening brace and the prelude picked
    up is the real selector.
    """
    return [(m.group(1).strip(), m.group(2))
            for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css)]


def _selectors(prelude: str) -> set[str]:
    return {s.strip() for s in prelude.split(",") if s.strip()}


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
    css = _strip_comments(css)

    timed = []
    for m in TRANSITION.finditer(css):
        decl = m.group(1).strip()
        literal = [ms(v, u) for v, u in DURATION.findall(decl)]
        tokens = CUSTOM_PROP.findall(decl)
        if any(d > 0 for d in literal) or tokens:
            timed.append((decl, tokens))

    # KEYFRAME ANIMATIONS, added by the director's ruling on P4.1 review-stop
    # finding 1. Until then this function scanned `transition:` declarations
    # ONLY, so both v1.1 animations were invisible to it: deleting the lever's
    # `--motion-vt: 0ms` left A3.5 running at full 250ms for a visitor who had
    # asked for reduced motion, and this checker printed "motion is switchable
    # off (C-10)" and exited 0. The gate was blind exactly where the new motion
    # lived. That demonstration is now the permanent negative control below.
    scan = _without_keyframes(css)
    body = reduced_motion_body(scan)
    reduce_rules = _innermost_rules(body) if body else []

    # A selector whose animation is switched off inside the lever block.
    killed: set[str] = set()
    for prelude, decls in reduce_rules:
        if re.search(r"animation(?:-duration)?\s*:\s*(none|0m?s)\b", decls, re.I):
            killed |= _selectors(prelude)

    animated = []
    if body is not None:
        outside = scan.replace(body, " ")
    else:
        outside = scan
    for prelude, decls in _innermost_rules(outside):
        for m in re.finditer(r"animation(?:-duration)?\s*:\s*([^;}]+)", decls, re.I):
            decl = m.group(1).strip()
            if decl.lower().startswith("none"):
                continue
            animated.append((prelude, decl, CUSTOM_PROP.findall(decl)))

    if not timed and not animated:
        return []

    if body is None:
        return [("MOTION_NOT_REDUCED",
                 "motion ships but there is no @media "
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

    # An animation is neutralised either by a token the lever zeroes, or by its
    # own selector being switched off inside the lever block. A3.5 uses the
    # first (--motion-vt); A3.6 must use the second, because a scroll-scrubbed
    # animation has no duration token to zero.
    for prelude, decl, tokens in animated:
        if set(tokens) & zeroed:
            continue
        if _selectors(prelude) & killed:
            continue
        problems.append((
            "MOTION_NOT_REDUCED",
            f"'{prelude}' animates ('{decl}') but reduced motion neither "
            f"zeroes a token it reads nor sets animation: none for it (C-10)"))
    return problems


# Properties that change how text composites against the background, and so
# change its contrast ratio. Deliberately a blunt list rather than an attempt to
# compute the composited ratio: CSS alone cannot tell which tokens a selector's
# subtree actually renders, so a checker that tried to do the arithmetic would
# be guessing with more decimal places. Refusing the channel is the honest move.
CONTRAST_AFFECTING = {"opacity", "color", "filter",
                      "background-color", "background", "mix-blend-mode"}


def check_scrubbed_contrast(css: str, rows: list[dict] | None = None
                            ) -> list[tuple[str, str]]:
    """Defect D-51's class, made structural instead of audit-caught.

    A scrubbed animation has no transient frames: progress is bound to scroll
    position, so EVERY point in its range is a resting state and must satisfy
    every static condition, contrast included. D-51 shipped
    `from { opacity: 0 }` on rows carrying --dim metadata, and --dim drops below
    AA at any alpha under 0.854 — a state the reader could sit in for as long as
    they left the scroll there. axe caught it at deploy; this catches it at
    build.

    Range-tuning is not a remedy and this checker deliberately offers no way to
    express one: narrowing `animation-range` changes WHICH scroll positions
    produce a failing state, never WHETHER one exists.

    THE ESCAPE, and why it exists: an entry may declare `contrast_proof` naming
    the computed floor at which every participating token still passes AA. That
    keeps this from being a rule obeyable only by never fading anything — but it
    costs a stated calculation, which is the point. Standing rule:
    docs/decisions/STEP-08-P4.1-SCRUBBED-STATES.md
    """
    rows = spec_rows() if rows is None else rows
    problems = []
    for row in rows:
        if row.get("duration_type") != "scrubbed":
            continue
        if row.get("contrast_proof"):
            continue
        for name in row.get("keyframes", []):
            m = re.search(rf"@keyframes\s+{re.escape(name)}\b", css, re.I)
            if not m:
                continue
            brace = css.find("{", m.end())
            if brace == -1:
                continue
            for prop in DECLARATION.findall(_block_after(css, brace + 1)):
                if prop.lower() in CONTRAST_AFFECTING:
                    problems.append((
                        "SCRUBBED_CONTRAST_RISK",
                        f"{row['id']} is scrubbed and @keyframes {name} animates "
                        f"'{prop.lower()}', so a reader can rest at any "
                        f"intermediate value. Remove the channel, or declare "
                        f"contrast_proof with the computed floor at which every "
                        f"participating token still meets AA (D-51)"))
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


def check_keyframes(css: str, declared: dict[str, str] | None = None
                    ) -> list[tuple[str, str]]:
    """C-12, both directions, over keyframe animations.

    Until the v1.1 amendment this refused EVERY `@keyframes` unconditionally,
    because the site shipped none and "zero keyframes" was therefore a true and
    cheap invariant. A3.5 and A3.6 make it false, so the sweep now asks the
    same question the id list is asked: does what ships match what is declared,
    in both directions?

      - a @keyframes no A3 entry claims   -> UNDECLARED_ANIMATION
      - a keyframes name an entry claims,
        with no @keyframes shipping it    -> UNSHIPPED_ANIMATION

    The second direction is the one that matters. Without it, deleting the CSS
    for a declared animation would leave /audit publishing an animation that no
    longer exists, and nothing would notice.
    """
    declared = declared_keyframes() if declared is None else declared
    shipped = set(KEYFRAMES.findall(css))

    problems = []
    for extra in sorted(shipped - set(declared)):
        problems.append(("UNDECLARED_ANIMATION",
                         f"@keyframes {extra} ships but no entry in "
                         f"audit-spec.json declares it"))
    for missing in sorted(set(declared) - shipped):
        problems.append(("UNSHIPPED_ANIMATION",
                         f"{declared[missing]} declares keyframes "
                         f"'{missing}' but no @keyframes of that name ships"))
    return problems


def check_keyframe_properties(css: str) -> list[tuple[str, str]]:
    """C-15 inside the keyframes themselves.

    check_transitions() enforces C-15's transform/opacity rule over
    `transition:` declarations. Nothing enforced it over keyframe animations,
    because none shipped. Now that two do, the A2.1 row on /audit — "motion
    uses transform / opacity only", reported as PASS on this checker's exit
    code — would be reporting a gate that never looked at the new motion.
    That is the D-48 disease, so the check follows the motion.

    Only the animatable properties are permitted; `animation-timeline` and
    friends are not animated properties and never appear inside a keyframe.
    """
    problems = []
    for m in KEYFRAMES.finditer(css):
        name = m.group(1)
        brace = css.find("{", m.end())
        if brace == -1:
            continue
        for prop in DECLARATION.findall(_block_after(css, brace + 1)):
            prop = prop.lower()
            if prop.startswith("--") or prop in ANIMATABLE:
                continue
            problems.append((
                "FORBIDDEN_PROPERTY",
                f"@keyframes {name} animates '{prop}'; C-15 permits only "
                f"{' and '.join(sorted(ANIMATABLE))}"))
    return problems


def shipped_ids(css: str) -> set[str]:
    """Which declared animations are actually implemented.

    DEFECT D-49, found in P4.1 and fixed here. This previously matched any
    occurrence of `A3.N` anywhere in the stylesheet, including ordinary prose
    inside comments. Every implementation block in this file discusses other
    entries by id in passing, so the UNSHIPPED_ANIMATION direction could be
    satisfied by *mentioning* an id rather than by implementing it — the exact
    "satisfied by wishful thinking" failure the old docstring claimed to
    prevent. It was caught red-handed: a comment in tokens.css reading
    "A3.6 is scrubbed" made the gate report A3.6 as shipped while no A3.6 CSS
    existed at all.

    The marker is now an explicit token that never occurs in prose. Writing
    `@ships A3.5` is a deliberate act; writing "A3.5" while explaining
    something is not.
    """
    return set(SHIPS.findall(css))


def spec_rows() -> list[dict]:
    return json.loads(SPEC.read_text(encoding="utf-8"))["a3_animations"]


def declared_keyframes() -> dict[str, str]:
    """Keyframe name -> the A3 entry that claims it.

    Declaring keyframes per entry is what lets the sweep below be
    two-directional. Without it the gate can only ask "is this @keyframes
    allowed at all", which is a question with no wrong answer once any
    keyframes ship.
    """
    return {name: row["id"]
            for row in spec_rows()
            for name in row.get("keyframes", [])}


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
                + check_keyframe_properties(css)
                + check_scrubbed_contrast(css)
                + check_list_agreement(css)
                + check_reduced_motion(css) + check_native_scroll(css, js))

    declared = declared_ids()
    kf = declared_keyframes()
    print(f"declared animations ({len(declared)}): {', '.join(declared)}")
    print(f"implemented in CSS  : {', '.join(sorted(shipped_ids(css))) or 'none found'}"
          f"   (marked '@ships A3.N', never a bare mention — D-49)")
    print(f"declared keyframes  : {', '.join(f'{n} [{i}]' for n, i in sorted(kf.items())) or 'none'}")
    print(f"shipped keyframes   : {', '.join(sorted(set(KEYFRAMES.findall(css)))) or 'none'}")
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
        # Marker updated to the D-49 convention. The old form was
        # "/* A3.9 rogue */", which no longer marks anything as shipped — and
        # this control failing was how that change announced itself.
        ("an undeclared animation MUST trip",
         lambda: check_list_agreement("/* @ships A3.9 rogue */ .x{opacity:0}"),
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

        # THE POISONED FIXTURE (director's condition, P4.1 review stop).
        # This is not a hypothetical: it is the exact shape of the repository
        # at the moment the gate was proved blind. A3.5 shipped reading
        # --motion-vt, the lever zeroed --motion-reveal and NOT --motion-vt,
        # and the checker reported "motion is switchable off (C-10)" and exited
        # 0 while a reduced-motion visitor got the full 250ms turn. The gate's
        # negative control IS the failure that exposed it, so it can never go
        # blind that way again without this failing first.
        ("POISONED FIXTURE — an animation reading an UNZEROED token MUST trip",
         lambda: check_reduced_motion(
             "::view-transition-old(page-content){"
             "animation: vt-turn-out var(--motion-vt) ease both}"
             "@media (prefers-reduced-motion: reduce){:root{--motion-reveal:0ms}}"),
         "MOTION_NOT_REDUCED", True),
        ("the SAME fixture with the token zeroed MUST NOT trip",
         lambda: check_reduced_motion(
             "::view-transition-old(page-content){"
             "animation: vt-turn-out var(--motion-vt) ease both}"
             "@media (prefers-reduced-motion: reduce){"
             ":root{--motion-reveal:0ms;--motion-vt:0ms}}"),
         "MOTION_NOT_REDUCED", False),
        ("a scrubbed animation with NO kill rule MUST trip (A3.6's shape)",
         lambda: check_reduced_motion(
             "@supports (animation-timeline: view()){"
             ".xp-row{animation: xp-surface auto linear both;"
             "animation-timeline: view()}}"
             "@media (prefers-reduced-motion: reduce){:root{--motion-reveal:0ms}}"),
         "MOTION_NOT_REDUCED", True),
        ("the same scrubbed animation WITH animation:none MUST NOT trip",
         lambda: check_reduced_motion(
             "@supports (animation-timeline: view()){"
             ".xp-row{animation: xp-surface auto linear both;"
             "animation-timeline: view()}}"
             "@media (prefers-reduced-motion: reduce){"
             ":root{--motion-reveal:0ms}.xp-row{animation:none}}"),
         "MOTION_NOT_REDUCED", False),

        # D-51 made structural (director's ruling, approved as designed).
        ("a SCRUBBED entry fading text MUST trip — this is D-51 itself",
         lambda: check_scrubbed_contrast(
             "@keyframes xp-surface{from{opacity:0;transform:translateY(12px)}}",
             [{"id": "A3.6", "duration_type": "scrubbed",
               "keyframes": ["xp-surface"]}]),
         "SCRUBBED_CONTRAST_RISK", True),
        ("the SHIPPED transform-only version MUST NOT trip",
         lambda: check_scrubbed_contrast(
             "@keyframes xp-surface{from{transform:translateY(12px)}}",
             [{"id": "A3.6", "duration_type": "scrubbed",
               "keyframes": ["xp-surface"]}]),
         "SCRUBBED_CONTRAST_RISK", False),
        ("a declared contrast_proof MUST allow the channel through",
         lambda: check_scrubbed_contrast(
             "@keyframes xp-surface{from{opacity:0.9}}",
             [{"id": "A3.6", "duration_type": "scrubbed",
               "keyframes": ["xp-surface"],
               "contrast_proof": "--dim meets AA at alpha >= 0.854"}]),
         "SCRUBBED_CONTRAST_RISK", False),
        ("a TIMED entry fading text MUST NOT trip — A3.5 is passed through",
         lambda: check_scrubbed_contrast(
             "@keyframes vt-turn-out{to{opacity:0}}",
             [{"id": "A3.5", "duration_type": "ms",
               "keyframes": ["vt-turn-out"]}]),
         "SCRUBBED_CONTRAST_RISK", False),

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

        # Keyframes, both directions (v1.1 amendment, ruling condition 1).
        ("an UNDECLARED @keyframes MUST still trip",
         lambda: check_keyframes("@keyframes rogue{from{opacity:0}}",
                                 {"vt-turn-in": "A3.5"}),
         "UNDECLARED_ANIMATION", True),
        ("a DECLARED @keyframes MUST NOT trip",
         lambda: check_keyframes("@keyframes vt-turn-in{from{opacity:0}}",
                                 {"vt-turn-in": "A3.5"}),
         "UNDECLARED_ANIMATION", False),
        ("a declared keyframes that does NOT ship MUST trip",
         lambda: check_keyframes("/* nothing here */",
                                 {"vt-turn-in": "A3.5"}),
         "UNSHIPPED_ANIMATION", True),
        ("a keyframe animating a forbidden property MUST trip (C-15)",
         lambda: check_keyframe_properties("@keyframes k{from{width:0}}"),
         "FORBIDDEN_PROPERTY", True),
        ("a keyframe animating transform/opacity MUST NOT trip (C-15)",
         lambda: check_keyframe_properties(
             "@keyframes k{from{opacity:0;transform:translateY(12px)}}"),
         "FORBIDDEN_PROPERTY", False),

        # D-49, both directions. The bug this replaces made every one of these
        # ids "shipped" by being mentioned, which is why the marker is explicit.
        ("an id merely MENTIONED in prose MUST NOT count as shipped (D-49)",
         lambda: check_list_agreement(
             "/* A3.6 is scrubbed to scroll position, unlike A3.1 */"),
         "UNSHIPPED_ANIMATION", True),
        ("an id marked '@ships' MUST count as shipped (D-49)",
         lambda: [p for p in check_list_agreement(
             "/* @ships A3.1 @ships A3.2 @ships A3.3 "
             "@ships A3.4 @ships A3.5 @ships A3.6 */")],
         "UNSHIPPED_ANIMATION", False),
    ]
    for label, fn, reason, must_trip in cases:
        found = reason in [r for r, _ in fn()]
        good = found == must_trip
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] "
              f"{'refused' if found else 'accepted':<8} {label}")

    # Positive control at repo level.
    real = check_transitions(css_text()) + check_keyframes(css_text()) + \
        check_keyframe_properties(css_text()) + \
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
