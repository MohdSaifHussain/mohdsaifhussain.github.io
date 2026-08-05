"""The site's own suite.  P3.1 / D9 (added deliverable, director-approved).

POLICY, approved 2026-08-06: one test per GATE BEHAVIOUR — each reason code's
negative control plus its positive control — never one test per assertion.
Splitting assertions to inflate a count would be exactly the overclaiming C-27
forbids, on the site whose whole purpose is demonstrating that we don't.

So the number this file reports is a number about coverage of behaviours, and
it publishes on /audit only alongside a statement of what it covers.

Every gate appears TWICE by design:
  - a negative control: input it MUST refuse, with the right reason code;
  - a positive control: real input it MUST accept.
A gate that refuses everything passes every negative control ever written.
"""

from __future__ import annotations

import json
import pathlib
import re

import pytest

import build
import subset_fonts

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(scope="session")
def site() -> pathlib.Path:
    """Build once for the whole session; return _site."""
    assert build.build() == 0, "the real build must succeed"
    return build.OUT


def reasons(found: list[tuple[str, str]]) -> list[str]:
    return [r for r, _ in found]


# ----------------------------------------------------- negative controls ---

def test_color_literal_hex_refused():
    assert "COLOR_LITERAL" in reasons(build.gate_color_literal("a{color:#ff0000}", "x"))


def test_color_literal_rgba_refused():
    assert "COLOR_LITERAL" in reasons(build.gate_color_literal("a{color:rgba(1,2,3,.4)}", "x"))


def test_unknown_token_refused():
    found = build.gate_unknown_token("a{color:var(--nope)}", {"--bg"}, "x")
    assert "TOKEN_UNKNOWN" in reasons(found)


def test_inline_style_refused():
    assert "INLINE_STYLE" in reasons(build.gate_inline('<p style="color:red">x</p>', "x"))


def test_inline_script_refused():
    assert "INLINE_SCRIPT" in reasons(build.gate_inline("<script>alert(1)</script>", "x"))


def test_mark_drift_viewbox_refused():
    html = ('<svg class="mark" viewBox="0 0 12 12"></svg>'
            '<svg class="mark" viewBox="0 0 16 16"></svg>')
    assert "MARK_DRIFT" in reasons(build.gate_mark_drift(html, "x"))


def test_mark_drift_stroke_refused():
    html = ('<svg class="mark"><path stroke-width="1.7"/></svg>'
            '<svg class="mark"><path stroke-width="2.4"/></svg>')
    assert "MARK_DRIFT" in reasons(build.gate_mark_drift_paths(html, "x"))


def test_mark_source_second_definition_refused():
    """D-14's added condition: exactly one place may emit a mark."""
    two = '<svg class="mark"></svg><svg class="mark"></svg>'
    assert "MARK_SOURCE" in reasons(build.gate_mark_source(two, {}))


def test_mark_source_rogue_template_refused():
    found = build.gate_mark_source('<svg class="mark"></svg>',
                                   {"rogue.j2": '<svg class="mark mark--check"></svg>'})
    assert "MARK_SOURCE" in reasons(found)


def test_anchor_missing_refused():
    """Contract 3.3 — a figure with no version anchor or no evidence link is a
    claim without a source, which is what defect D-02 was about."""
    snap = {"repos": {"known": {"anchor": "v1", "anchor_url": "https://x/1"}}}

    no_link = [{"id": "p", "links": {}}]
    assert "STAT_UNANCHORED" in reasons(build.gate_anchors(no_link, snap))

    not_in_snapshot = [{"id": "p", "links": {"repo": "https://github.com/o/unknown"}}]
    assert "STAT_UNANCHORED" in reasons(build.gate_anchors(not_in_snapshot, snap))

    half = {"repos": {"known": {"anchor": "v1", "anchor_url": ""}}}
    has_repo = [{"id": "p", "links": {"repo": "https://github.com/o/known"}}]
    assert "STAT_UNANCHORED" in reasons(build.gate_anchors(has_repo, half)), (
        "an anchor without an evidence link must still refuse")


def test_asset_missing_refused():
    found = build.gate_assets([(ROOT / "no-such-dir", ROOT / "out")])
    assert "ASSET_MISSING" in reasons(found)


def test_data_missing_refused(tmp_path):
    with pytest.raises(build.BuildRefused) as e:
        build.load_data(tmp_path)
    assert e.value.reason == "DATA_MISSING"


def test_data_malformed_refused(tmp_path):
    for name in build.DATA_FILES:
        (tmp_path / f"{name}.json").write_text("{}", encoding="utf-8")
    (tmp_path / "profile.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(build.BuildRefused) as e:
        build.load_data(tmp_path)
    assert e.value.reason == "DATA_MALFORMED"


def test_template_missing_refused():
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader(str(build.TPL)))
    with pytest.raises(build.BuildRefused) as e:
        build.get_template_or_refuse(env, "no-such-template.j2")
    assert e.value.reason == "TEMPLATE_MISSING"


def _complete_synthetic_cmaps() -> dict[str, set[int]]:
    """A cmap set that satisfies every requirement — built, not loaded."""
    return {stem: set(subset_fonts.REQUIRED[family])
            for stem, (_rel, family, *_r) in subset_fonts.FACES.items()}


def test_font_coverage_gate_detects_missing_glyph():
    """Negative control driven by a SYNTHETIC poisoned cmap.

    Defect D-18: this used to assert `0x2717 not in <a real font>`, which tests
    a property of the fixture rather than the gate, depends on gitignored files,
    and would fail for the wrong reason if that glyph were ever added. Removing
    one required codepoint from a synthetic complete set proves the gate finds
    exactly that gap — identically on any machine, with no files and no network.
    """
    cmaps = _complete_synthetic_cmaps()
    assert subset_fonts.find_gaps(cmaps) == [], "synthetic complete set must be clean"

    cmaps["IBMPlexMono-Regular"].discard(0x2713)
    assert subset_fonts.find_gaps(cmaps) == [("IBMPlexMono-Regular", 0x2713)]


# ----------------------------------------------------- positive controls ---

def test_real_site_css_has_no_colour_literal():
    css = (ROOT / "static/css/site.css").read_text(encoding="utf-8")
    assert build.gate_color_literal(css, "site.css") == []


def test_real_macros_has_no_colour_literal():
    src = (ROOT / "templates/_macros.html.j2").read_text(encoding="utf-8")
    assert build.gate_color_literal(src, "_macros") == []


def test_real_css_tokens_all_defined():
    tokens = (ROOT / "static/css/tokens.css").read_text(encoding="utf-8")
    site = (ROOT / "static/css/site.css").read_text(encoding="utf-8")
    defined = {m.group(1) for m in build.VAR_DEF.finditer(tokens)}
    assert build.gate_unknown_token(site, defined, "site.css") == []
    assert build.gate_unknown_token(tokens, defined, "tokens.css") == []


def test_real_marks_resolve_from_single_source():
    macros = (ROOT / "templates/_macros.html.j2").read_text(encoding="utf-8")
    others = {p.name: p.read_text(encoding="utf-8")
              for p in sorted(build.TPL.glob("*.j2")) if p.name != "_macros.html.j2"}
    assert build.gate_mark_source(macros, others) == []


def test_html_entity_is_not_a_colour_literal():
    """Regression for D-19: `&#8599;` (the ↗ entity) has the exact shape of a
    4-digit hex colour, and the gate false-refused valid markup. A gate that
    refuses valid input is as broken as one that accepts invalid input."""
    assert build.gate_color_literal("<a>&#8599; &#183; &#8212;</a>", "x") == []
    assert "COLOR_LITERAL" in reasons(build.gate_color_literal("a{color:#8599}", "x")), (
        "the real 4-digit hex form must still refuse")


def test_real_projects_all_anchored():
    data = build.load_data()
    snapshot = build.load_snapshot()
    assert build.gate_anchors(data["projects"]["projects"], snapshot) == []


def test_real_asset_trees_present():
    assert build.gate_assets(build.asset_sources()) == []


def test_real_data_loads():
    assert set(build.load_data()) == set(build.DATA_FILES)


def test_shipped_fonts_carry_every_required_glyph():
    """Every codepoint the design uses is present in the SHIPPED subset of the
    face that needs it.

    This is the test that matters: it asserts a property of the artifact the
    browser downloads, so a subsetting bug that dropped a glyph fails here.
    The previous version read the upstream TTFs and would have passed (D-18)."""
    _cmaps, gaps = subset_fonts.shipped_coverage()
    assert gaps == [], f"missing glyphs: {[(s, hex(c)) for s, c in gaps]}"


# ------------------------------------------- properties of the real output --

def test_build_is_deterministic(site):
    first = build.tree_hash()
    assert build.build() == 0
    assert build.tree_hash() == first


def test_output_has_no_inline_style_or_script(site):
    for page in sorted(site.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        assert build.gate_inline(html, page.name) == []


def test_counts_render_from_data_not_literals(site):
    """Regression for D-15: Jinja binds | looser than %, so
    `'%02d' % projects | length` silently formats the LIST and takes the
    string's length. This asserts the rendered number equals the real one."""
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    flagship = [p for p in data["projects"] if p.get("flagship")]
    home = (site / "index.html").read_text(encoding="utf-8")
    assert f"ENTRIES {len(flagship):02d}" in home

    listing = (site / "projects/index.html").read_text(encoding="utf-8")
    assert f"{len(data['projects']):02d} ENTRIES" in listing


def test_no_third_party_resources_load(site):
    """C-04 and C-19 as a passing test: **zero third-party resources load**.

    This checks only things the browser FETCHES — script/img/source src, and
    <link href> (stylesheets, preloads, icons). Every one must be a same-origin
    relative path. An outbound <a href> is navigation, not a loaded resource,
    and is governed separately by C-20; conflating the two made one test answer
    two different conditions and produced a false failure on the owner's own
    Pages origin.

    The day a real third-party resource appears, this fails and forces the
    claim to be rewritten rather than quietly outliving its truth (rule 8).
    """
    fetched = re.compile(
        r'<(?:script|img|source|iframe)\b[^>]*\ssrc="([^"]+)"'
        r'|<link\b[^>]*\shref="([^"]+)"', re.I)
    for page in sorted(site.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        for m in fetched.finditer(html):
            url = m.group(1) or m.group(2)
            assert not re.match(r"https?://|//", url), (
                f"{page.name}: third-party resource {url}")


def test_outbound_links_are_allowlisted(site):
    """C-20 / charter §2: outbound navigation goes only where the charter says.

    mohdsaifhussain.github.io is the site's OWN origin — other repos' Pages
    sites live there — so it is not third-party. Listed explicitly rather than
    waved through, so adding a new destination is a deliberate act.
    """
    allowed = re.compile(
        r"https://(www\.linkedin\.com|github\.com|ghcr\.io|mohdsaifhussain\.github\.io)/")
    for page in sorted(site.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        for m in re.finditer(r'<a\b[^>]*\shref="(https?://[^"]+)"', html):
            assert allowed.match(m.group(1)), f"{page.name}: unlisted {m.group(1)}"


def test_every_page_has_exactly_one_h1(site):
    """C-24."""
    for page in sorted(site.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        assert len(re.findall(r"<h1\b", html)) == 1, f"{page.name}"


def test_every_page_declares_lang_and_landmarks(site):
    """C-11 lang, C-24 landmarks."""
    for page in sorted(site.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        assert '<html lang="en">' in html, f"{page.name}"
        for tag in ("<header", "<nav", "<main", "<footer"):
            assert tag in html, f"{page.name} missing {tag}"


def test_external_links_carry_noopener(site):
    """C-20."""
    for page in sorted(site.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        for m in re.finditer(r'<a\b[^>]*href="https?://[^"]+"[^>]*>', html):
            assert 'rel="noopener noreferrer"' in m.group(), f"{page.name}: {m.group()}"
