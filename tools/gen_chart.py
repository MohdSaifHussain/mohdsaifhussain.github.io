"""Generate the inline chart figure under templates/figures/.  P5.9 / D2.

WHAT THIS IS. prevalence-kit publishes exactly one image in its README,
`demo/coverage_curve.svg`. The owner ruled on 2026-09-01 that this entry carries
that image instead of an architecture diagram, and that it must work in light,
dark and high contrast. This tool performs that adaptation MECHANICALLY, so the
result is a recolour anyone can verify rather than a redrawing anyone must
trust.

WHY IT IS INLINE AND NOT A SERVED FILE. An `<img src="...svg">` is a separate
document. It cannot resolve the host page's custom properties, so it could never
follow the theme, and in dark mode it would render as a white slab. Inline SVG
is the only construction that themes, and it is what the six architecture
diagrams already do.

WHAT CHANGES, AND NOTHING ELSE
  - Every colour attribute is replaced by a class. Colour then comes from
    site.css, which is where contract 3.2 requires every colour to live.
  - The opaque white ground rect is deleted, so the page's own background shows
    through. Painting it var(--bg) instead would defeat forced-colours mode.
  - The root font-family is dropped; the family comes from .chart in site.css.
  - The Wilson series is dashed. Under `forced-colors: active` the browser
    repaints both series to CanvasText, so a hue-only distinction is no
    distinction at all: WCAG 2.2 SC 1.4.1 needs a second, non-colour channel.
    https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html
    The pattern is deliberately not the nominal line's own `6 4`.
  - The four lines of PROSE leave the drawing and are rendered as HTML beside
    it. This is not a preference. SVG text cannot wrap: it is laid out on one
    line at a fixed coordinate, and the root <svg> clips to its viewport, so an
    overrun is silently CUT OFF rather than merely ugly. Measured in a browser
    on 2026-09-01, against the 760-unit box:

        line          in the source's Georgia      in this site's mono
        title  y=24    ends  497.2   fits           ends  627.2   fits
        sub    y=42    ends  636.7   fits           ends  805.4   over by  45.4
        note   y=436   ends  952.6   over by 192.6  ends 1196.0   over by 436.0
        note   y=454   ends  633.1   fits           ends  850.4   over by  90.4

    Stated in that direction deliberately: ONE line overran in the source and
    THREE overrun here, so this site's wider monospace widened an inherited
    problem rather than merely inheriting it. An earlier note in this file put
    all three overruns on the source, by applying the monospace advance to
    Georgia as well; that arithmetic was wrong and the browser is the
    correction. Held
    as HTML the same words wrap, stay selectable, and are read as text by a
    screen reader at every viewport. The words, and their order, are the
    source's own; tests/test_chart.py re-derives all four from the source SVG
    and refuses if the copy in projects.json has drifted by one character.

WHAT DOES NOT CHANGE. Every coordinate, every path, every data point, every
word, every font-size and every stroke-width is carried across untouched, and
tests/test_chart.py re-derives them from the source to prove it.

READING R-P5.9-1 — why the font-size attributes stay. Contract 3.2 bars type
steps outside tokens.css. A font-size inside a viewBox is not a type step: it is
a drawing coordinate in the artifact's own space, scaled by the browser to
whatever width the figure gets. Rewriting those to the site's scale would
redraw the chart, which is the thing the owner ruled against. They stay, and
this paragraph is the reason they stay.

Usage (PowerShell):
    python tools\\gen_chart.py
    python tools\\gen_chart.py --selftest
"""

from __future__ import annotations

import argparse
import hashlib
import html
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")     # defect D-13
sys.stderr.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "reference" / "prevalence-kit-coverage-source.svg"
OUT = ROOT / "templates" / "figures" / "prevalence-kit-coverage.svg.j2"

# The source is a committed artifact, not a moving target. Recorded 2026-09-01
# from prevalence-kit demo/coverage_curve.svg at origin/main 6155194, verified
# byte-identical to the working tree at C:\Users\mohds\prevalence-kit.
SRC_SHA256 = "ab49ab4d6aadae780a8f67cf42dadb03ac136c4506da258c636475de67a57113"

# The one sentence a screen reader gets. It states what the figure shows and
# what it settles, at the width of the evidence: four pre-registered points,
# not a swept grid. Wording drawn from the README's own paragraph.
TITLE = ("Interval coverage on Civil Comments at four pre-registered "
         "thresholds: Clopper-Pearson covers at or above its nominal 95% at "
         "all four, paying in width as the rate rarefies, while Wilson sits "
         "below nominal at the two commoner rates and above it at the two "
         "rarer.")

# colour -> the class that replaces it. Every entry is exercised; a colour in
# the source with no entry here refuses the generation rather than passing
# through as a literal.
COLOURS = {
    "#1a1a1a": "ink",
    "#555555": "c-note",
    "#999999": "c-dim",
    "#e0e0e0": "c-grid",
    "#f0f0f0": "c-grid c-grid--v",
    "#b34700": "wilson",
    "#1a5fb4": "cp",
}

# What each class must appear exactly this many times in the output. These are
# counted from the source, and a mismatch refuses: it is how a source that
# changed under us fails loudly instead of silently producing a different
# picture.
EXPECT = {
    "c-legend": 2, "c-note": 9, "c-dim": 4,
    "c-grid": 9, "c-grid--v": 4, "c-nominal": 1,
    "c-series c-wilson": 2, "c-err c-wilson": 4, "c-dot c-wilson": 4,
    "c-series c-cp": 2, "c-err c-cp": 4, "c-dot c-cp": 4,
}

# The prose lines, named by the y coordinate they sit at in the source. These
# leave the drawing (see the header). Identified by coordinate rather than by
# their text so that a wording change upstream cannot slip past unnoticed: the
# digest guard catches the change, and this list still finds the right lines.
PROSE_Y = ('y="24"', 'y="42"', 'y="436"', 'y="454"')

HEX = re.compile(r"#[0-9a-fA-F]{3,8}")
COLOUR_ATTR = re.compile(r'\s(?:fill|stroke)="(#[0-9a-fA-F]{3,8})"')
GROUND = '<rect width="760" height="470" fill="#ffffff"/>'


class ChartRefused(Exception):
    def __init__(self, reason: str, detail: str):
        super().__init__(f"REASON={reason}\n  {detail}")
        self.reason = reason


def text_of(line: str) -> str:
    """The text content of a one-line <text> element, entities resolved."""
    m = re.search(r">([^<]*)</text>", line)
    if not m:
        raise ChartRefused("CHART_PROSE", f"no text content in: {line[:70]}")
    return html.unescape(m.group(1))


def prose() -> list[str]:
    """The four prose lines, in the source's own document order.

    Public because tests/test_chart.py and nothing else is allowed to decide
    what those sentences say: they are re-derived here, from the source, on
    every run.
    """
    lines = load_source().strip().split("\n")
    out = [text_of(ln.strip()) for ln in lines
           if ln.strip().startswith("<text") and any(y in ln for y in PROSE_Y)]
    if len(out) != len(PROSE_Y):
        raise ChartRefused("CHART_PROSE", f"found {len(out)}, expected {len(PROSE_Y)}")
    return out


# Room left above the topmost and below the lowest retained coordinate. The
# lower figure is the larger because the coordinates down there are text
# BASELINES, and a baseline is not the bottom of its glyphs.
PAD_TOP, PAD_BOTTOM = 14, 16


def crop_box(kept: list[str]) -> tuple[str, float, float]:
    """The viewBox that fits what is left, once the prose has gone.

    The source's box is 760x470 because it had a title and a subtitle above the
    plot and two footnotes below. With those lifted out, roughly a quarter of
    the drawing is empty, which on a phone costs the plot the height it most
    needs. So the box is cropped VERTICALLY to the content that remains, and
    the horizontal extent is left exactly as the source drew it.

    Nothing here moves a datum: the coordinates are untouched and the window
    onto them narrows. The bounds are computed from the retained elements, so
    an element that later moves outside them changes this box rather than
    being quietly clipped by it.
    """
    ys: list[float] = []
    for line in kept:
        for m in re.finditer(r'\b(?:y|y1|y2|cy)="(-?[\d.]+)"', line):
            ys.append(float(m.group(1)))
        d = re.search(r'\sd="([^"]+)"', line)
        if d:
            ys += [float(pt.split(",")[1]) for pt in re.findall(r"[\d.]+,[\d.]+", d.group(1))]
    if not ys:
        raise ChartRefused("CHART_CROP", "no y coordinates found in the retained elements")
    top, bottom = min(ys) - PAD_TOP, max(ys) + PAD_BOTTOM
    return f"0 {top:g} 760 {bottom - top:g}", top, bottom


def classify(line: str, colour: str) -> str:
    """Which class this element gets, from the colour plus what the element is.

    The colour alone is not enough: #1a1a1a is the title, the legend labels and
    the nominal reference line, three different roles. The title has already
    left as prose by the time this runs, so what remains under that colour is
    the reference line and the two legend labels.
    """
    slot = COLOURS[colour]
    if slot == "ink":
        return "c-nominal" if line.startswith("<line") else "c-legend"
    if slot in ("wilson", "cp"):
        series = "c-wilson" if slot == "wilson" else "c-cp"
        if line.startswith("<circle"):
            return f"c-dot {series}"
        # The error bars are the thin ones; the data path and the legend swatch
        # share the heavy weight, and so share a class.
        if 'stroke-width="1.4"' in line:
            return f"c-err {series}"
        return f"c-series {series}"
    return slot


def transform(src: str) -> str:
    lines = src.strip().split("\n")
    if not lines[0].startswith("<svg") or lines[-1] != "</svg>":
        raise ChartRefused("CHART_SHAPE", "the source is not a single <svg> element")

    out: list[str] = []
    dropped_ground = 0
    dropped_prose: list[str] = []
    for line in lines[1:-1]:
        line = line.strip()
        if line == GROUND:
            dropped_ground += 1
            continue
        if line.startswith("<text") and any(y in line for y in PROSE_Y):
            dropped_prose.append(text_of(line))
            continue
        m = COLOUR_ATTR.search(line)
        if not m:
            raise ChartRefused("CHART_UNCOLOURED",
                               f"no fill/stroke to map, so its role is unknown: {line[:70]}")
        colour = m.group(1)
        if colour not in COLOURS:
            raise ChartRefused("CHART_COLOUR_UNKNOWN",
                               f"{colour} has no class; add it to COLOURS: {line[:70]}")
        cls = classify(line, colour)
        # Drop the colour attribute, then insert the class immediately after the
        # tag name. Every other attribute survives byte-for-byte.
        stripped = line[:m.start()] + line[m.end():]
        tag = re.match(r"<([a-z]+)", stripped)
        if not tag:
            raise ChartRefused("CHART_SHAPE", f"not an element: {stripped[:70]}")
        out.append(f'<{tag.group(1)} class="{cls}"' + stripped[tag.end():])

    if dropped_ground != 1:
        raise ChartRefused("CHART_GROUND",
                           f"expected exactly one white ground rect, found {dropped_ground}")
    if len(dropped_prose) != len(PROSE_Y):
        raise ChartRefused("CHART_PROSE",
                           f"expected {len(PROSE_Y)} prose lines to lift out, "
                           f"found {len(dropped_prose)}")

    box, top, bottom = crop_box(out)
    svg = "\n".join([
        # role="img" plus a labelling <title> is how the six diagrams announce
        # themselves; the same treatment here, so the figure is one object to a
        # screen reader rather than fifty unlabelled shapes.
        f'<svg class="chart" viewBox="{box}" role="img"'
        ' aria-labelledby="pk-coverage-title" xmlns="http://www.w3.org/2000/svg">',
        f'<title id="pk-coverage-title">{TITLE}</title>',
        *out,
        "</svg>",
    ]) + "\n"

    # The crop must not clip anything. Read the coordinates back out of the
    # FINISHED text and check each against the box that same text declares,
    # rather than trusting the numbers that produced it (doctrine rule 13).
    declared = re.search(r'viewBox="0 (-?[\d.]+) 760 ([\d.]+)"', svg)
    if not declared:
        raise ChartRefused("CHART_CROP", "the output declares no readable viewBox")
    y0 = float(declared.group(1))
    y1 = y0 + float(declared.group(2))
    body = [ln for ln in svg.split("\n") if ln.startswith(("<line", "<text", "<circle", "<path"))]
    for ln in body:
        for m in re.finditer(r'\b(?:y|y1|y2|cy)="(-?[\d.]+)"', ln):
            if not y0 <= float(m.group(1)) <= y1:
                raise ChartRefused("CHART_CROP",
                                   f"{m.group(1)} falls outside the declared box "
                                   f"[{y0:g}, {y1:g}]: {ln[:70]}")
    if len(body) != len(out):
        raise ChartRefused("CHART_CROP",
                           f"{len(out)} elements went in and {len(body)} came back out")

    left = HEX.search(svg)
    if left:
        raise ChartRefused("COLOR_LITERAL",
                           f"{left.group()} survived; build.py would refuse this template")

    counts = {k: len(re.findall(rf'class="{re.escape(k)}"', svg)) for k in EXPECT}
    # c-grid and c-grid--v share a class attribute, so count the token instead.
    counts["c-grid"] = len(re.findall(r'class="c-grid[ "]', svg))
    counts["c-grid--v"] = len(re.findall(r'c-grid--v', svg))
    wrong = {k: (counts[k], v) for k, v in EXPECT.items() if counts[k] != v}
    if wrong:
        raise ChartRefused("CHART_COUNT",
                           "; ".join(f"{k}: got {g}, expected {e}" for k, (g, e) in wrong.items()))
    return svg


def load_source() -> str:
    if not SRC.exists():
        raise ChartRefused("CHART_SOURCE_MISSING", str(SRC))
    raw = SRC.read_bytes()
    got = hashlib.sha256(raw).hexdigest()
    if got != SRC_SHA256:
        raise ChartRefused("CHART_SOURCE_CHANGED",
                           f"expected {SRC_SHA256}, got {got}. If the upstream figure "
                           f"genuinely changed, re-verify it and update SRC_SHA256 in "
                           f"the same commit.")
    return raw.decode("utf-8")


def selftest() -> int:
    """Both controls. A generator that has only ever succeeded proves nothing."""
    cases = [
        ("CHART_COLOUR_UNKNOWN",
         '<svg>\n<rect width="760" height="470" fill="#ffffff"/>\n'
         '<line x1="1" stroke="#123456"/>\n</svg>'),
        ("CHART_GROUND", '<svg>\n<text fill="#555555">x</text>\n</svg>'),
        ("CHART_SHAPE", '<div>x</div>'),
        ("CHART_UNCOLOURED",
         '<svg>\n<rect width="760" height="470" fill="#ffffff"/>\n'
         '<line x1="1" y1="2"/>\n</svg>'),
    ]
    bad = 0
    for want, src in cases:
        try:
            transform(src)
        except ChartRefused as e:
            got = e.reason
        else:
            got = "ACCEPTED"
        ok = got == want
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} negative control {want}: {got}")

    # The positive control: a gate that refuses everything proves nothing either.
    try:
        transform(load_source())
    except ChartRefused as e:
        print(f"  FAIL positive control: the real source was refused: {e}")
        bad += 1
    else:
        print("  ok   positive control: the real source is accepted")
    print("SELFTEST OK" if not bad else f"SELFTEST FAILED ({bad})")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    try:
        svg = transform(load_source())
    except ChartRefused as e:
        print(e, file=sys.stderr)
        return 2
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg, encoding="utf-8", newline="\n")
    print(f"CHART OK  {OUT.relative_to(ROOT)}  ({len(svg.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
