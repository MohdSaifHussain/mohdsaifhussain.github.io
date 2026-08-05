"""C-09 contrast, RECOMPUTED from tokens.css.  P3.4 / D7.

Charter C-09: body text ≥ 4.5:1 (AA), and ≥ 7:1 "wherever the monochrome
palette permits (AAA 1.4.6, adopted as target, not claim)".

Director's Q3 ruling, 2026-08-06: report per-token measured ratios WITH usage
context; claim AA in full; state plainly which tokens reach 7:1 and which do
not. The charter's target stays visible as a target — neither claimed nor
quietly dropped.

WHY RECOMPUTE (doctrine rule 13). The handoff states ratios: ink 15.9:1,
body 10.6:1, bright 13.6:1, dim 5.1:1, accent 9.3:1. Those are CLAIMS. This
tool derives every ratio from the hex values actually in tokens.css by the
WCAG 2.2 relative-luminance formula, and prints the handoff's figure beside it
so any disagreement is visible rather than inherited.

Usage context matters (requirement 3.4): WCAG's threshold depends on text size
and weight. Large text is >= 24px, or >= 18.66px bold. A ratio quoted without
the size it is used at is not a conformance statement.

Usage (PowerShell):
    python tools\\check_contrast.py
    python tools\\check_contrast.py --selftest
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")     # defect D-13
sys.stderr.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS = ROOT / "static" / "css" / "tokens.css"

AA_NORMAL, AA_LARGE = 4.5, 3.0
AAA_NORMAL, AAA_LARGE = 7.0, 4.5

# (foreground token, background, px, bold, where it is used, handoff's claim)
PAIRS = [
    ("--ink",    "--bg", 62,   False, "display-xl — home identity line",      15.9),
    ("--ink",    "--bg", 34,   False, "display-lg — page h1",                 15.9),
    ("--ink",    "--bg", 17,   False, "wordmark-nav",                         15.9),
    ("--body",   "--bg", 12.5, False, "mono-body-sm — receipts, method",      10.6),
    ("--body",   "--bg", 15,   False, "quote-sm — problem statements",        10.6),
    ("--bright", "--bg", 12.5, False, "metric text — evidence rows",          13.6),
    ("--dim",    "--bg", 11.5, False, "mono-meta — metadata strips",           5.1),
    ("--dim",    "--bg", 10,   True,  "mono-label — small-caps section labels", 5.1),
    ("--accent", "--bg", 11,   True,  "mono-link — REPO, VERIFY CREDENTIAL",   9.3),
    ("--accent", "--bg", 44,   False, "numeral — entry numbers",               9.3),
    ("--bg", "--accent", 11,   True,  "skip link, PDF button hover (inverted)", None),
]


def parse_tokens() -> dict[str, str]:
    text = TOKENS.read_text(encoding="utf-8")
    return {m.group(1): m.group(2)
            for m in re.finditer(r"^\s*(--[\w-]+):\s*(#[0-9a-fA-F]{3,8})\s*;", text, re.M)}


def to_rgb(hex_colour: str) -> tuple[int, int, int]:
    h = hex_colour.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    """WCAG 2.2 relative luminance."""
    out = []
    for channel in rgb:
        c = channel / 255
        out.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = out
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg: str, bg: str) -> float:
    l1, l2 = relative_luminance(to_rgb(fg)), relative_luminance(to_rgb(bg))
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def is_large(px: float, bold: bool) -> bool:
    return px >= 24 or (bold and px >= 18.66)


def evaluate() -> tuple[list[dict], list[tuple[str, str]]]:
    tokens = parse_tokens()
    rows, problems = [], []
    for fg_name, bg_name, px, bold, usage, claimed in PAIRS:
        if fg_name not in tokens or bg_name not in tokens:
            problems.append(("TOKEN_UNKNOWN", f"{fg_name} or {bg_name} not in tokens.css"))
            continue
        r = ratio(tokens[fg_name], tokens[bg_name])
        large = is_large(px, bold)
        aa = r >= (AA_LARGE if large else AA_NORMAL)
        aaa = r >= (AAA_LARGE if large else AAA_NORMAL)
        rows.append({"fg": fg_name, "bg": bg_name, "hex": tokens[fg_name], "px": px,
                     "bold": bold, "large": large, "ratio": r, "aa": aa, "aaa": aaa,
                     "usage": usage, "claimed": claimed})
        if not aa:
            problems.append(("CONTRAST_BELOW_AA",
                             f"{fg_name} on {bg_name} at {px}px = {r:.2f}:1, "
                             f"below the {'large' if large else 'normal'}-text AA floor"))
    return rows, problems


def run() -> int:
    rows, problems = evaluate()

    print("C-09 contrast, recomputed from tokens.css (WCAG 2.2 relative luminance)\n")
    print(f"{'token':<10}{'hex':<10}{'size':<12}{'measured':>10}  {'AA':<5}{'7:1':<6}usage")
    print("-" * 100)
    for r in rows:
        size = f"{r['px']:g}px{' bold' if r['bold'] else ''}{' L' if r['large'] else ''}"
        print(f"{r['fg']:<10}{r['hex']:<10}{size:<12}{r['ratio']:>9.2f}:1  "
              f"{'PASS' if r['aa'] else 'FAIL':<5}{'yes' if r['aaa'] else 'no':<6}{r['usage']}")

    print("\nAgainst the handoff's stated figures (claims, not inputs):")
    for r in rows:
        if r["claimed"] is None:
            continue
        delta = abs(r["ratio"] - r["claimed"])
        flag = "" if delta < 0.15 else "   <-- DISAGREES"
        print(f"  {r['fg']:<10} handoff {r['claimed']:>5.1f}:1   measured {r['ratio']:>5.2f}:1{flag}")

    aaa_yes = sorted({r["fg"] for r in rows if r["aaa"]})
    aaa_no = sorted({r["fg"] for r in rows if not r["aaa"]})
    print("\nC-09 as claimed (director's Q3 ruling):")
    print(f"  AA — claimed in full: every pair meets its threshold: "
          f"{'YES' if not problems else 'NO'}")
    print(f"  7:1 target reached  : {', '.join(aaa_yes) or 'none'}")
    print(f"  7:1 target NOT met  : {', '.join(aaa_no) or 'none'}"
          "   (a target the charter set, stated plainly, neither claimed nor dropped)")

    if problems:
        print("\nCONTRAST CHECK FAILED")
        for reason, detail in problems:
            print(f"  REASON={reason}  {detail}")
        return 1
    print("\nCONTRAST OK — every pair meets AA at the size it is used")
    return 0


def selftest() -> int:
    ok = True
    print("SELFTEST\n")

    known = [("#ffffff", "#000000", 21.0), ("#000000", "#000000", 1.0),
             ("#777777", "#ffffff", 4.48)]
    for fg, bg, expected in known:
        got = ratio(fg, bg)
        good = abs(got - expected) < 0.02
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {fg} on {bg}: {got:.2f}:1 (expect {expected})")

    # Negative control: a pair that must be refused.
    saved = PAIRS[:]
    PAIRS.append(("--rule-mid-fake", "--bg", 12, False, "poison", None))
    PAIRS[-1] = ("--dim", "--dim", 12, False, "poison: dim on dim", None)
    _rows, problems = evaluate()
    tripped = "CONTRAST_BELOW_AA" in [r for r, _ in problems]
    ok = ok and tripped
    print(f"  [{'PASS' if tripped else 'FAIL'}] negative control: an identical "
          f"foreground/background pair is refused")
    PAIRS[:] = saved

    # Positive control: the real palette must not trip.
    _rows, problems = evaluate()
    clean = not problems
    ok = ok and clean
    print(f"  [{'PASS' if clean else 'FAIL'}] positive control: the real palette is accepted")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    return selftest() if args.selftest else run()


if __name__ == "__main__":
    raise SystemExit(main())
