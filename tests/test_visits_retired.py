"""P5.2 (STEP-11, decision 5.2.1): the visit counter is retired. No page may
carry one, faked or dashed, and its limitation A4.4 sits in the resolved
register, not the active one."""
from __future__ import annotations

import json
import pathlib

import pytest

import build

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def site() -> pathlib.Path:
    assert build.build() == 0
    return build.OUT


def test_no_page_carries_a_visit_counter(site):
    pages = list(site.rglob("*.html"))
    assert pages, "the build produced pages"
    for page in pages:
        html = page.read_text(encoding="utf-8")
        assert "VISITS" not in html, page
        assert "foot-visits" not in html, page


def test_a4_4_is_resolved_not_active():
    spec = json.loads((ROOT / "data/audit-spec.json").read_text(encoding="utf-8"))
    active = {r["id"] for r in spec["a4_limitations"]}
    resolved = {r["id"]: r for r in spec["a4_resolved"]}
    assert "A4.4" not in active
    assert resolved["A4.4"]["closed"] == "2026-08-22"


def test_site_css_has_no_orphaned_visits_rule():
    css = (ROOT / "static/css/site.css").read_text(encoding="utf-8")
    assert ".foot-visits" not in css
