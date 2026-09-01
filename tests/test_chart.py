"""P5.9: the chart figure is a recolour of the repository's own SVG, and stays one.

The point of these tests is the one thing a reader has to take on trust
otherwise: that "we only changed the colours" is true. So the geometry is
re-derived from the committed source and compared against the committed
output, by a parser written here rather than by calling the generator's own
transform — a test that re-runs the code under test proves only that the code
is deterministic.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import gen_chart  # noqa: E402

OUT = ROOT / "templates" / "figures" / "prevalence-kit-coverage.svg.j2"
FIGURES = ROOT / "templates" / "figures"

# The attributes that carry colour in the source. Everything else is geometry
# or type and must survive untouched.
COLOUR_ATTRS = ("fill", "stroke")
# [a-z0-9-] and not [a-z-]: x1, y1, x2, y2, cx and cy all carry a digit,
# and a pattern without one silently drops every coordinate on every line
# and circle -- which is to say it makes the test below pass while testing
# nothing. Caught by the negative control, 2026-09-01.
ATTR = re.compile(r'([a-z][a-z0-9-]*)="([^"]*)"')
ELEMENT = re.compile(r"<(line|text|circle|path|rect)\b([^>]*?)/?>(?:([^<]*)</\1>)?")


def parse(text: str) -> list[tuple[str, dict[str, str], str]]:
    """Every drawn element as (tag, attributes, text content)."""
    out = []
    for m in ELEMENT.finditer(text):
        attrs = dict(ATTR.findall(m.group(2)))
        out.append((m.group(1), attrs, (m.group(3) or "").strip()))
    return out


def geometry(el: tuple[str, dict[str, str], str]) -> tuple:
    """An element stripped of everything the recolour was allowed to touch."""
    tag, attrs, text = el
    kept = {k: v for k, v in attrs.items()
            if k not in COLOUR_ATTRS and k != "class"}
    # fill="none" is not a colour; it is "this shape is a stroke, not a blob",
    # and it must survive. The generator keeps it as an attribute.
    if attrs.get("fill") == "none":
        kept["fill"] = "none"
    return (tag, tuple(sorted(kept.items())), text)


@pytest.fixture(scope="module")
def source_kept() -> list:
    """The source elements that were meant to survive: everything but the
    opaque ground and the four lines of prose."""
    src = gen_chart.load_source()
    prose = set(gen_chart.prose())
    out = []
    for el in parse(src):
        tag, attrs, text = el
        if tag == "rect" and attrs.get("fill") == "#ffffff":
            continue          # the ground, deliberately dropped
        if tag == "text" and text in prose:
            continue          # lifted into HTML, tested separately below
        out.append(el)
    return out


def test_committed_chart_matches_its_generator():
    """The file on disk is the generator's output, not something hand-edited."""
    assert OUT.read_text(encoding="utf-8") == gen_chart.transform(gen_chart.load_source()), \
        "run python tools/gen_chart.py"


def test_no_colour_literal_survives_in_any_figure():
    """build.py's colour gate globs templates/*.j2 and does NOT recurse, so a
    hex in a subdirectory template would reach the page unchallenged. This is
    that gate, for this subdirectory (observation 5.9.4)."""
    for f in sorted(FIGURES.glob("*.svg.j2")):
        found = re.findall(r"#[0-9a-fA-F]{3,8}", f.read_text(encoding="utf-8"))
        assert not found, f"{f.name}: colour literal {found}"


def test_every_element_survives_the_recolour(source_kept):
    """Same elements, same count, same order. Nothing added, nothing lost."""
    got = parse(OUT.read_text(encoding="utf-8"))
    assert len(got) == len(source_kept), \
        f"{len(source_kept)} elements in the source, {len(got)} in the output"
    assert [g[0] for g in got] == [s[0] for s in source_kept], "element order changed"


def test_every_coordinate_and_word_survives_the_recolour(source_kept):
    """The load-bearing one: every coordinate, every path, every remaining word
    is identical. If this passes, "only the colours changed" is a fact."""
    got = [geometry(el) for el in parse(OUT.read_text(encoding="utf-8"))]
    want = [geometry(el) for el in source_kept]
    assert got == want


def test_the_coordinate_check_can_fail(source_kept):
    """Negative control. A check that has only ever passed is a decoration."""
    tampered = [geometry(el) for el in source_kept]
    tag, attrs, text = tampered[0]
    key = next(k for k, _ in attrs if k.startswith("y")) if attrs else None
    assert key, "the first element carries no y coordinate to move"
    tampered[0] = (tag, tuple((k, "999" if k == key else v) for k, v in attrs), text)
    assert tampered != [geometry(el) for el in source_kept], \
        "moving a coordinate did not change the comparison"


def test_the_two_series_are_told_apart_without_colour():
    """WCAG 2.2 SC 1.4.1. Under forced colours both series are repainted to one
    system colour, so the dash is the only thing left distinguishing them, and
    it must reach the legend swatch as well as the data path."""
    css = (ROOT / "static" / "css" / "site.css").read_text(encoding="utf-8")
    assert re.search(r"\.c-series\.c-wilson\s*\{[^}]*stroke-dasharray", css), \
        "the Wilson series carries no non-colour distinction"
    svg = OUT.read_text(encoding="utf-8")
    swatches = [ln for ln in svg.split("\n")
                if ln.startswith("<line") and 'class="c-series' in ln]
    assert len(swatches) == 2, "expected one legend swatch per series"
    assert sum('c-wilson' in s for s in swatches) == 1


def test_figure_prose_is_the_sources_own_words():
    """The four lines moved out of the drawing into projects.json. They are the
    source's, character for character, and drift fails here."""
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    entries = [p for p in data["projects"] if p.get("figure")]
    assert entries, "no entry declares a figure; this test would be vacuous"
    title, subtitle, note1, note2 = gen_chart.prose()
    for p in entries:
        assert p["figure"]["title"] == title, p["id"]
        assert p["figure"]["subtitle"] == subtitle, p["id"]
        assert p["figure"]["notes"] == [note1, note2], p["id"]


def test_every_declared_figure_exists_and_is_cited():
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    for p in data["projects"]:
        if "figure" not in p:
            continue
        assert (FIGURES / f"{p['figure']['file']}.svg.j2").exists(), p["id"]
        src = p["figure"]["source"]
        assert "gen_chart.py" in src and "origin/main" in src, \
            f"{p['id']}: the figure must cite where it came from"


def test_every_live_entry_carries_a_figure_or_a_diagram():
    """The invariant projects.json `_status` states since P5.9. It was 'every
    live entry carries a diagram' until this phase widened it, and a widened
    invariant nobody checks is an invariant that has quietly lapsed."""
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    live = [p for p in data["projects"]
            if not p.get("case_study") and not p.get("archived")]
    assert live, "no live entries; this test would be vacuous"
    for p in live:
        assert p.get("diagram") or p.get("figure"), \
            f"{p['id']}: a live entry carries one or the other"


def test_the_chart_does_not_animate():
    """diagram.js selects `.diagram`. A figure classed `.chart` is never armed,
    which is what keeps A3.7's declared ledger true without a new entry."""
    svg = OUT.read_text(encoding="utf-8")
    assert 'class="chart"' in svg
    assert "diagram" not in svg.split("\n")[0], "the chart must not be a .diagram"
    assert "data-post" not in svg
