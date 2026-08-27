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
import json
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


THEMES = ("dark", "light", "dark-hc", "light-hc")
# P5.7: the two high-contrast palettes are the colour palettes with the
# --<theme>-hc-* tokens laid over them, exactly as the CSS mapping does it.
HC_OVERLAY = {"--body": "--hc-body", "--dim": "--hc-dim", "--accent": "--hc-accent"}

# P4.2. Each palette declares its own prefixed tokens, so the two are read as
# two. The previous parser regexed `--name: #hex;` flat across the whole file
# into one dict, which was correct while one palette existed and became a trap
# the moment a second did: later matches win, so a light `:root` would have
# silently overwritten the dark values and the checker would have reported ONE
# palette as THE palette, passing while measuring the wrong thing.
PALETTE_TOKEN = re.compile(
    r"^\s*--(dark|light)-([\w-]+):\s*(#[0-9a-fA-F]{3,8})\s*;", re.M)


def parse_palettes() -> dict[str, dict[str, str]]:
    """{theme: {semantic token: hex}} — read from the --dark-*/--light-* pairs.

    Returns the SEMANTIC name (`--bg`), not the prefixed one, because that is
    what PAIRS and the rest of the site speak. The prefix exists only to keep
    the two palettes distinguishable in a single file.
    """
    text = TOKENS.read_text(encoding="utf-8")
    out: dict[str, dict[str, str]] = {t: {} for t in THEMES}
    for theme, name, hex_value in PALETTE_TOKEN.findall(text):
        out[theme][f"--{name}"] = hex_value
    for base in ("dark", "light"):
        hc = dict(out[base])
        for semantic, source in HC_OVERLAY.items():
            if source in out[base]:
                hc[semantic] = out[base][source]
        out[f"{base}-hc"] = hc
    return out


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


def evaluate(palettes: dict[str, dict[str, str]] | None = None
             ) -> tuple[list[dict], list[tuple[str, str]]]:
    """Every pair, in every theme, plus the three cross-theme constraints.

    The constraints are the owner's, and each has its own reason code so a
    refusal says which promise broke:
      AA in full, at the size each pair is used            CONTRAST_BELOW_AA
      7:1 in light wherever DARK reaches it                SEVEN_TO_ONE_LOST
      light --dim no worse than dark's measured 5.78:1     DIM_WORSENED
    """
    palettes = parse_palettes() if palettes is None else palettes
    rows, problems = [], []
    per_theme: dict[str, list[dict]] = {}

    for theme in THEMES:
        tokens = palettes.get(theme, {})
        theme_rows = []
        for fg_name, bg_name, px, bold, usage, claimed in PAIRS:
            if fg_name not in tokens or bg_name not in tokens:
                problems.append(("TOKEN_UNKNOWN",
                                 f"[{theme}] {fg_name} or {bg_name} has no "
                                 f"--{theme}- value in tokens.css"))
                continue
            r = ratio(tokens[fg_name], tokens[bg_name])
            large = is_large(px, bold)
            aa = r >= (AA_LARGE if large else AA_NORMAL)
            aaa = r >= (AAA_LARGE if large else AAA_NORMAL)
            theme_rows.append({
                "theme": theme, "fg": fg_name, "bg": bg_name,
                "hex": tokens[fg_name], "bg_hex": tokens[bg_name], "px": px,
                "bold": bold, "large": large, "ratio": r, "aa": aa, "aaa": aaa,
                "usage": usage,
                # The handoff states dark figures only. Light rows carry no
                # claim rather than an invented one.
                "claimed": claimed if theme == "dark" else None})
            if not aa:
                problems.append(("CONTRAST_BELOW_AA",
                                 f"[{theme}] {fg_name} on {bg_name} at {px}px = "
                                 f"{r:.2f}:1, below the "
                                 f"{'large' if large else 'normal'}-text AA floor"))
        per_theme[theme] = theme_rows
        rows.extend(theme_rows)
        # P5.7: a high-contrast palette must reach AAA on every pair, which is
        # the whole promise the toggle and the OS setting make.
        if theme.endswith("-hc"):
            for r in theme_rows:
                if not r["aaa"]:
                    problems.append(("HC_BELOW_AAA",
                                     f"[{theme}] {r['fg']} on {r['bg']} at {r['px']}px = "
                                     f"{r['ratio']:.2f}:1, below WCAG 1.4.6 (7:1 normal, "
                                     f"4.5:1 large) in a high-contrast palette"))

    # --- cross-theme constraints -----------------------------------------
    # Both lists walk PAIRS in the same order, so they pair up positionally.
    # If a theme dropped a row for a missing token the lengths differ, and
    # that is already a TOKEN_UNKNOWN above; zip stops rather than mispairing.
    for dark_row, light_row in zip(per_theme.get("dark", []),
                                   per_theme.get("light", [])):
        if dark_row["aaa"] and not light_row["aaa"]:
            problems.append((
                "SEVEN_TO_ONE_LOST",
                f"{dark_row['fg']} on {dark_row['bg']} at {dark_row['px']}px "
                f"reaches 7:1 in dark ({dark_row['ratio']:.2f}:1) but not in "
                f"light ({light_row['ratio']:.2f}:1) — light mode may not cost "
                f"a target the dark theme already meets"))
        if dark_row["fg"] == "--dim" and light_row["ratio"] < dark_row["ratio"] - 0.005:
            problems.append((
                "DIM_WORSENED",
                f"--dim at {dark_row['px']}px measures {light_row['ratio']:.2f}:1 "
                f"in light against {dark_row['ratio']:.2f}:1 in dark. --dim is the "
                f"one token below 7:1; its shortfall may not deepen"))
    return rows, problems


def summary_line(rows: list[dict]) -> str:
    """The one-line claim /audit publishes, DERIVED.

    Defect D-55: this string was a hard-coded literal in write_audit.py,
    including the figure "5.78:1" typed by hand. A published number with no
    producer behind it is D-52's family, and it would have gone on reading 5.78
    however the palette changed.
    """
    parts = []
    for theme in THEMES:
        theme_rows = [r for r in rows if r["theme"] == theme]
        if not theme_rows:
            continue
        short = sorted({f"{r['fg']} ({r['ratio']:.2f}:1)"
                        for r in theme_rows if not r["aaa"]})
        parts.append(f"{theme}: AA met; "
                     + (f"7:1 met except {', '.join(short)}" if short
                        else "7:1 met in full"))
    return " · ".join(parts)


def run(json_out: pathlib.Path | None = None) -> int:
    rows, problems = evaluate()

    print("C-09 contrast, recomputed from tokens.css (WCAG 2.2 relative luminance)")
    print("Four palettes: dark, light, and each with high contrast (P4.2, P5.7).\n")
    print(f"{'theme':<7}{'token':<10}{'hex':<10}{'on':<10}{'size':<12}"
          f"{'measured':>10}  {'AA':<5}{'7:1':<6}usage")
    print("-" * 118)
    for r in rows:
        size = f"{r['px']:g}px{' bold' if r['bold'] else ''}{' L' if r['large'] else ''}"
        print(f"{r['theme']:<7}{r['fg']:<10}{r['hex']:<10}{r['bg_hex']:<10}{size:<12}"
              f"{r['ratio']:>9.2f}:1  {'PASS' if r['aa'] else 'FAIL':<5}"
              f"{'yes' if r['aaa'] else 'no':<6}{r['usage']}")

    print("\nAgainst the handoff's stated figures (claims, not inputs; dark only —")
    print("the handoff states no light figures, so light rows carry no claim):")
    for r in rows:
        if r["claimed"] is None:
            continue
        delta = abs(r["ratio"] - r["claimed"])
        flag = "" if delta < 0.15 else "   <-- DISAGREES"
        print(f"  {r['fg']:<10} handoff {r['claimed']:>5.1f}:1   measured {r['ratio']:>5.2f}:1{flag}")

    print("\nC-09 as claimed (director's Q3 ruling), per theme:")
    for theme in THEMES:
        theme_rows = [r for r in rows if r["theme"] == theme]
        if not theme_rows:
            continue
        yes = sorted({r["fg"] for r in theme_rows if r["aaa"]})
        no = sorted({r["fg"] for r in theme_rows if not r["aaa"]})
        print(f"  [{theme}] 7:1 reached: {', '.join(yes) or 'none'}")
        print(f"  [{theme}] 7:1 NOT met: {', '.join(no) or 'none'}")
    print("  (a target the charter set, stated plainly, neither claimed nor dropped)")

    if json_out:
        payload = {
            "_generated": ("Machine-written by tools/check_contrast.py, recomputed "
                           "from the hex values in tokens.css by the WCAG 2.2 "
                           "relative-luminance formula. Never hand-edited."),
            "themes": list(THEMES),
            "summary": summary_line(rows),
            "rows": rows,
        }
        json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8", newline="\n")
        print(f"\n  written to {json_out}")

    if problems:
        print("\nCONTRAST CHECK FAILED")
        for reason, detail in problems:
            print(f"  REASON={reason}  {detail}")
        return 1
    print("\nCONTRAST OK — every pair meets AA at the size it is used, in BOTH "
          "themes;\n              light loses no 7:1 the dark theme reaches, --dim "
          "does not worsen,\n              and both high-contrast palettes reach AAA on every pair")
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

    # --- P4.2: the two palettes are read as TWO -------------------------
    real = parse_palettes()
    distinct = (real.get("dark") and real.get("light")
                and real["dark"] != real["light"])
    ok = ok and bool(distinct)
    print(f"  [{'PASS' if distinct else 'FAIL'}] two palettes parsed, and they "
          f"differ (dark {len(real.get('dark', {}))} tokens, "
          f"light {len(real.get('light', {}))})")

    # The trap the old flat parser would have fallen into: if the two themes
    # were collapsed, the same pair would measure IDENTICALLY in both. This
    # asserts they do not, on the real file.
    rows, _ = evaluate()
    by_theme = {t: [r["ratio"] for r in rows if r["theme"] == t] for t in THEMES}
    not_collapsed = by_theme["dark"] != by_theme["light"]
    ok = ok and not_collapsed
    print(f"  [{'PASS' if not_collapsed else 'FAIL'}] the themes are not collapsed "
          f"— the same pairs measure differently in each")

    # Negative controls for each cross-theme constraint, on synthetic palettes
    # so they exercise the rule rather than the current values.
    base_dark = dict(real["dark"])
    def synth(**light_overrides):
        light = dict(real["light"]); light.update(light_overrides)
        return {"dark": base_dark, "light": light}

    for label, override, reason in (
        ("a light --accent below 7:1 where dark reaches it",
         {"--accent": "#8d6e2e"}, "SEVEN_TO_ONE_LOST"),
        ("a light --dim worse than dark's 5.78:1",
         {"--dim": "#7a786f"}, "DIM_WORSENED"),
        ("a light --body below the AA floor",
         {"--body": "#cfccc3"}, "CONTRAST_BELOW_AA"),
    ):
        _r, probs = evaluate(synth(**override))
        tripped = reason in [p for p, _ in probs]
        ok = ok and tripped
        print(f"  [{'PASS' if tripped else 'FAIL'}] {label} -> {reason}")

    # Positive control: the real palettes must not trip.
    _rows, problems = evaluate()
    clean = not problems
    ok = ok and clean
    print(f"  [{'PASS' if clean else 'FAIL'}] positive control: both real palettes "
          f"are accepted{'' if clean else f' — {problems}'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json-out", type=pathlib.Path,
                    help="per-token measured ratios for both themes, for "
                         "tools/write_audit.py to publish (P4.2 / D-55)")
    args = ap.parse_args()
    return selftest() if args.selftest else run(args.json_out)


if __name__ == "__main__":
    raise SystemExit(main())
