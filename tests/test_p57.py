"""P5.7: light mode re-derived with dark as the base, and a high-contrast
layer reached by the OS setting or the toggle. Positive controls over the
real files; negative controls over fixtures."""
from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import check_contrast as cc  # noqa: E402

TOKENS = (ROOT / "static/css/tokens.css").read_text(encoding="utf-8")


def _blocks(css):
    media = re.search(r"@media \(prefers-contrast: more\)\s*\{\s*"
                      r":root:not\(\[data-contrast=\"normal\"\]\)\s*\{(.*?)\}", css, re.S)
    manual = re.search(r":root\[data-contrast=\"more\"\]\s*\{(.*?)\}", css, re.S)
    return [m.group(1) for m in (media, manual) if m]


def test_both_contrast_mappings_are_identical():
    blocks = _blocks(TOKENS)
    assert len(blocks) == 2
    norm = lambda b: sorted(l.strip() for l in b.split(";") if l.strip())
    assert norm(blocks[0]) == norm(blocks[1])


def test_every_pair_is_aaa_in_both_high_contrast_palettes():
    rows, problems = cc.evaluate()
    assert not [p for p in problems if p[0] == "HC_BELOW_AAA"], problems
    for r in rows:
        if r["theme"].endswith("-hc"):
            assert r["aaa"], r


def test_seven_to_one_is_met_in_full_in_both_colour_themes():
    """The site's one declared AAA shortfall, --dim, closed in P5.7."""
    rows, _ = cc.evaluate()
    for r in rows:
        if r["theme"] in ("dark", "light"):
            assert r["aaa"], f"{r['theme']} {r['fg']} {r['ratio']:.2f}"


def test_light_accent_reaches_parity_with_dark():
    rows, _ = cc.evaluate()
    dark = next(r for r in rows if r["theme"] == "dark" and r["fg"] == "--accent" and r["px"] == 44)
    light = next(r for r in rows if r["theme"] == "light" and r["fg"] == "--accent" and r["px"] == 44)
    assert light["ratio"] >= dark["ratio"] - 0.5


def test_hc_below_aaa_is_refused():
    """Negative control: a high-contrast dim that only reaches AA must trip."""
    pal = cc.parse_palettes()
    pal["light-hc"] = dict(pal["light-hc"], **{"--dim": "#64625c"})   # 5.79:1
    _, problems = cc.evaluate(pal)
    assert any(p[0] == "HC_BELOW_AAA" for p in problems)


def test_mono_weight_is_a_token_and_light_uses_medium():
    for name in ("--type-mono-body:", "--type-mono-body-sm:", "--type-mono-meta:", "--type-mono-meta-sm:"):
        for m in re.finditer(rf"^\s*{re.escape(name)}\s*([^;]+);", TOKENS, re.M):
            assert m.group(1).lstrip().startswith("var(--w-mono)"), (name, m.group(1))
    light_blocks = re.findall(r"data-theme=\"light\"\]\s*\{(.*?)\}", TOKENS, re.S)
    assert any("--w-mono:     500" in b for b in light_blocks)
    assert (ROOT / "static/assets/fonts/IBMPlexMono-Medium.woff2").exists() or \
           (ROOT / "assets/fonts/IBMPlexMono-Medium.woff2").exists()


def test_forced_colors_block_ships_and_toggle_markup_has_both_controls():
    css = (ROOT / "static/css/site.css").read_text(encoding="utf-8")
    assert "@media (forced-colors: active)" in css
    html = (ROOT / "templates/base.html.j2").read_text(encoding="utf-8")
    assert "data-theme-toggle" in html and "data-contrast-toggle" in html
    init = (ROOT / "static/js/theme-init.js").read_text(encoding="utf-8")
    assert 'getItem("contrast")' in init
