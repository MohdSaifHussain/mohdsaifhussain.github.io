"""P5.3 (STEP-12): mobile legibility tokens and the CSP connect-src change."""
from __future__ import annotations

import pathlib
import re

import build

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _block(css: str, query: str) -> str:
    i = css.index(query)
    depth = 0
    for k in range(i, len(css)):
        if css[k] == "{":
            depth += 1
        elif css[k] == "}":
            depth -= 1
            if depth == 0:
                return css[i:k]
    raise AssertionError("unterminated media block")


def test_small_mono_steps_are_12px_at_or_below_900px():
    css = (ROOT / "static/css/tokens.css").read_text(encoding="utf-8")
    mobile = _block(css, "@media (max-width: 900px)")
    for token in ("--type-mono-meta:", "--type-mono-meta-sm:", "--type-mono-link:"):
        m = re.search(rf"{re.escape(token)}\s+\d+\s+(\d+(?:\.\d+)?)px", mobile)
        assert m, f"{token} not redefined in the 900px block"
        assert float(m.group(1)) >= 12, token


def test_desktop_scale_unchanged():
    css = (ROOT / "static/css/tokens.css").read_text(encoding="utf-8")
    root = css[: css.index("@media")]
    assert "--type-mono-meta:    400 11.5px/1.6" in root
    assert "--type-mono-link:    600 11px/1" in root


def test_csp_connect_src_is_self_and_still_strict():
    v = build.csp_value()
    assert "connect-src 'self'" in v
    assert "'unsafe-inline'" not in v and "'unsafe-eval'" not in v
    assert "script-src 'self'" in v and "object-src 'none'" in v


def test_csp_negative_control_detects_a_loosened_policy():
    """The assertion above must be able to fail: a policy carrying
    'unsafe-inline' is exactly what it guards against."""
    loosened = build.csp_value().replace("script-src 'self'", "script-src 'self' 'unsafe-inline'")
    assert "'unsafe-inline'" in loosened
