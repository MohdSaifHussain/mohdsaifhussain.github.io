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
import sys

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

    This checks only things the browser FETCHES. An outbound <a href> is
    navigation, not a loaded resource, and is governed separately by C-20;
    conflating the two made one test answer two different conditions and
    produced a false failure on the owner's own Pages origin (defect D-20).

    Defect D-27: <link rel="canonical"> is metadata and MUST be absolute — the
    browser fetches nothing. Checking every <link href> flagged it, the same
    mistake as D-20 in a new place. "Resource" is therefore defined by what the
    browser actually FETCHES, enumerated by rel, not by attribute name.

    The day a real third-party resource appears, this fails and forces the
    claim to be rewritten rather than quietly outliving its truth (rule 8).
    """
    FETCHING_RELS = {"stylesheet", "preload", "prefetch", "preconnect",
                     "dns-prefetch", "icon", "apple-touch-icon", "manifest",
                     "modulepreload"}
    src_re = re.compile(r'<(?:script|img|source|iframe|embed)\b[^>]*\ssrc="([^"]+)"', re.I)
    link_re = re.compile(r"<link\b([^>]*)>", re.I)

    for page in sorted(site.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        for m in src_re.finditer(html):
            assert not re.match(r"https?://|//", m.group(1)), (
                f"{page.name}: third-party resource {m.group(1)}")
        for m in link_re.finditer(html):
            attrs = m.group(1)
            rels = set((re.search(r'\brel="([^"]+)"', attrs, re.I) or
                        re.match("", "")).group(1).lower().split()) \
                if re.search(r'\brel="', attrs, re.I) else set()
            if not (rels & FETCHING_RELS):
                continue                     # canonical, alternate: metadata
            href = re.search(r'\bhref="([^"]+)"', attrs, re.I)
            assert href and not re.match(r"https?://|//", href.group(1)), (
                f"{page.name}: third-party resource {href.group(1) if href else attrs}")


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


def test_some_page_carries_both_marks(site):
    """Obligation O-9 as a passing test.

    MARK_DRIFT can only fire where both marks appear together; on a page with
    one mark it is a decoration. At the P3.2 review stop that page was Projects
    (17 ✓ / 2 ✗). The owner then supplied TS-Sentry's metrics, which correctly
    removed the last ✗ from Projects, and coverage migrated to /audit, where
    the A4 limitations table carries the crosses.

    That migration is fine — but it must never silently become zero. This
    asserts some page still exercises the gate for real.
    """
    dual = []
    for page in sorted(site.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        svgs = re.findall(r'<svg[^>]*class="mark[^"]*"[^>]*>', html)
        if any("mark--check" in s for s in svgs) and any("mark--cross" in s for s in svgs):
            dual.append(page.name)
    assert dual, "no page carries both marks — MARK_DRIFT is unexercised on real output"


def test_verified_entries_render_a_check(site):
    """C-27 positive direction: every entry that HAS metrics shows the mark.

    Non-vacuous by construction — it asserts something for all five projects.
    """
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    html = (site / "projects/index.html").read_text(encoding="utf-8")
    cards = html.split('<article class="card">')[1:]
    assert len(cards) == len(data["projects"]), "card count must match the data"

    checked = 0
    for card, p in zip(cards, data["projects"]):
        if p.get("verified_metrics"):
            assert "mark--check" in card, f"{p['name']} has metrics but renders no check"
            checked += 1
    assert checked, "no project has metrics; this assertion would be vacuous"


def test_pending_entries_never_render_a_check(site):
    """C-27 negative direction: a ✓ must never sit on an entry whose metrics
    are pending. Defect D-25 was this failure in the Experience receipts.

    Defect D-32: the earlier version of this test looped over pending entries
    and, once the owner supplied TS-Sentry's metrics, that list became empty —
    so the loop body never ran and the test PASSED BY ASSERTING NOTHING. A test
    guarding against overclaiming that silently stopped guarding is the same
    failure as D-18.

    It now skips loudly when there is nothing to check, so the absence of
    coverage is visible in the test output instead of masquerading as a pass.
    """
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    pending = [p for p in data["projects"] if p.get("metrics_pending")]
    if not pending:
        pytest.skip("no entry currently has pending metrics — nothing to verify, "
                    "and this is reported rather than passed silently (D-32)")

    html = (site / "projects/index.html").read_text(encoding="utf-8")
    cards = html.split('<article class="card">')[1:]
    for card, p in zip(cards, data["projects"]):
        if p.get("metrics_pending"):
            assert "mark--check" not in card, (
                f"{p['name']} has pending metrics but renders a verification check")
            assert "mark--cross" in card, f"{p['name']} is pending but shows no cross"


def test_metrics_basis_agrees_with_entries():
    """STEP-05 §6, as a passing test (doctrine rule 8).

    Owner-measured counts for the remaining three projects are DEFERRED. While
    any entry is resume-baseline the basis sentence must be present; once none
    is, it must be gone. Today this passes on the first branch. The day the last
    entry is upgraded and the sentence is left behind, it fails — so a sentence
    describing a basis nobody uses cannot quietly outlive its own truth.
    """
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    basis = data["_metrics_basis"]
    owner_measured = {"ts-sentry"}
    any_resume_baseline = any(p["id"] not in owner_measured and p.get("verified_metrics")
                              for p in data["projects"])
    mentions = "resume-stated baselines" in basis
    assert mentions == any_resume_baseline, (
        "_metrics_basis and the entries disagree about which bases are in use: "
        f"sentence present={mentions}, resume-baseline entries exist={any_resume_baseline}")


def test_animation_list_matches_shipped(site):
    """C-12: the declared list and what ships agree, in both directions."""
    import subprocess
    r = subprocess.run([sys.executable, "tools/check_animations.py"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_evidence_layer_never_covers_the_links_column(site):
    """Requirement 3.3 — the defect the committed design was rebuilt to fix.

    Structural proof: the layer is pointer-events:none AND is bounded to end
    before the links column. Observed behaviour is the director's at the stop;
    this asserts the two properties that make it possible.
    """
    css = (ROOT / "static/css/site.css").read_text(encoding="utf-8")
    block = css.split(".evidence {", 1)[1].split("}", 1)[0]
    assert "pointer-events: none" in block
    assert "right: calc(220px" in block, "layer must stop short of the 220px links column"
    assert "left: calc(120px" in block, "layer must start after the 120px numeral column"

    html = (site / "index.html").read_text(encoding="utf-8")
    assert 'class="evidence" aria-hidden="true"' in html


def test_csp_present_and_strict(site):
    """C-18. The policy must be on every page, and must not weaken itself."""
    for page in sorted(site.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        m = re.search(r'http-equiv="Content-Security-Policy" content="([^"]+)"', html)
        assert m, f"{page.name}: no CSP meta"
        policy = m.group(1)
        for weakener in ("unsafe-inline", "unsafe-eval", "unsafe-hashes", "*"):
            assert weakener not in policy, f"{page.name}: CSP contains {weakener}"
        assert "&#" not in policy, (
            f"{page.name}: CSP contains an HTML entity — it must render literally, "
            "because meta CSP has no report-only mode to catch a mis-parse")
        for directive in ("default-src", "script-src", "style-src", "object-src", "base-uri"):
            assert directive in policy, f"{page.name}: CSP missing {directive}"


def test_csp_omits_directives_meta_ignores(site):
    """CSP Level 3 §3.3: report-uri, frame-ancestors and sandbox are IGNORED
    when delivered by meta. Writing one would look like protection while
    providing none, so their ABSENCE from the policy is the honest state and is
    asserted rather than left to drift back in."""
    html = (site / "index.html").read_text(encoding="utf-8")
    policy = re.search(r'http-equiv="Content-Security-Policy" content="([^"]+)"', html).group(1)
    for ignored in ("frame-ancestors", "report-uri", "sandbox"):
        assert ignored not in policy, (
            f"CSP declares {ignored}, which meta delivery ignores — "
            "declared protection that does not exist")


def test_contrast_recomputed_meets_aa():
    """C-09. Ratios come from tokens.css by the WCAG formula, never from the
    handoff's table — see STEP-02-HANDOFF Erratum 1, where every stated figure
    turned out to have been computed against a lighter background."""
    import subprocess
    r = subprocess.run([sys.executable, "tools/check_contrast.py"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_declared_limitations_reach_the_published_page(site):
    """Charter §8, as a passing test: a limitation declared in audit-spec.json
    must actually appear on /audit.

    A limit that exists only in a data file is a limit nobody is told about.
    This is what stops the screen-reader partial (A4.9) — or any future
    declaration — from being recorded internally and quietly not published.
    """
    spec = json.loads((ROOT / "data/audit-spec.json").read_text(encoding="utf-8"))
    html = (site / "audit/index.html").read_text(encoding="utf-8")
    for row in spec["a4_limitations"] + spec.get("a4_resolved", []):
        assert row["id"] in html, f"{row['id']} declared but absent from /audit"
    assert "A4.9" in html, "the screen-reader partial must be published"


def test_no_limitation_contradicts_the_data(site):
    """Defect D-37, as a passing test.

    /audit published "TS-Sentry metrics are unverified" for a full phase after
    the owner supplied them and the card started rendering a verification mark.
    A declared limit that has quietly stopped being true is the same failure as
    a test that has quietly stopped asserting (D-32), pointed the other way.

    A limit must leave the ACTIVE list when it closes — into the resolved list,
    never into nothing.
    """
    spec = json.loads((ROOT / "data/audit-spec.json").read_text(encoding="utf-8"))
    projects = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))

    active = " ".join(r["limitation"].lower() for r in spec["a4_limitations"])
    for p in projects["projects"]:
        if p.get("verified_metrics") and not p.get("metrics_pending"):
            name = p["name"].lower()
            assert not (name in active and "unverified" in active), (
                f"{p['name']} has metrics but an active limitation still calls "
                f"them unverified")


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


@pytest.mark.parametrize("tool", ["check_c33.py", "check_content.py"])
def test_checker_selftests_pass(tool, site):
    """Each checker proves its own controls. Their detailed control output is
    printed by the tools themselves and run in CI; these two tests assert the
    verdict so a broken checker fails the suite too.

    The suite count deliberately does NOT absorb every individual control
    inside those tools — inflating the number by re-counting assertions is the
    overclaiming C-27 forbids. /audit states what the count covers."""
    import subprocess
    r = subprocess.run([sys.executable, f"tools/{tool}", "--selftest"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("tool", ["check_c33.py", "check_content.py"])
def test_checkers_accept_the_real_repo(tool, site):
    """Positive control at the repo level: the checkers must not refuse the
    real thing, or they would be gates that refuse everything."""
    import subprocess
    r = subprocess.run([sys.executable, f"tools/{tool}"],
                       cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_external_links_carry_noopener(site):
    """C-20."""
    for page in sorted(site.rglob("*.html")):
        html = page.read_text(encoding="utf-8")
        for m in re.finditer(r'<a\b[^>]*href="https?://[^"]+"[^>]*>', html):
            assert 'rel="noopener noreferrer"' in m.group(), f"{page.name}: {m.group()}"
