"""P5.5: entries render newest push first, everywhere, from the snapshot's
pushed_at, with the date shown as ISO 8601 in a <time datetime>. Positive
controls over the real build; negative controls over fixtures."""
from __future__ import annotations

import json
import pathlib
import re

import pytest

import build

ROOT = pathlib.Path(__file__).resolve().parent.parent
ISO_INSTANT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


@pytest.fixture(scope="module")
def site() -> pathlib.Path:
    assert build.build() == 0
    return build.OUT


def _snapshot():
    return json.loads((ROOT / "data/generated/github.json").read_text(encoding="utf-8"))["repos"]


def _expected(entries):
    snap = _snapshot()
    def pushed(e):
        return snap[e["links"]["repo"].rstrip("/").rsplit("/", 1)[-1]]["pushed_at"]
    return [e["name"] for e in sorted(entries, key=pushed, reverse=True)]


def test_projects_page_is_newest_push_first(site):
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    html = (site / "projects/index.html").read_text(encoding="utf-8")
    names = re.findall(r'<h2 class="display-md">(.*?)</h2>', html)
    assert names == _expected(data["projects"])


def test_home_flagship_is_newest_push_first(site):
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    html = (site / "index.html").read_text(encoding="utf-8")
    names = re.findall(r'<span class="display-sm">(.*?)</span>', html)
    assert names == _expected([p for p in data["projects"] if p.get("flagship")])


def test_every_card_shows_its_push_date_as_iso_8601(site):
    for page, count_key in (("projects/index.html", None), ("index.html", "flagship")):
        html = (site / page).read_text(encoding="utf-8")
        times = re.findall(r'<time class="pushed mono-meta" datetime="([^"]+)">PUSHED (\d{4}-\d{2}-\d{2})</time>', html)
        assert times, page
        for instant, date in times:
            assert ISO_INSTANT.match(instant), instant
            assert instant.startswith(date)


def test_jsonld_date_matches_the_visible_one(site):
    html = (site / "projects/index.html").read_text(encoding="utf-8")
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
    ld_dates = [i["item"]["dateModified"] for i in ld["itemListElement"]]
    visible = re.findall(r'<time class="pushed mono-meta" datetime="([^"]+)"', html)
    assert ld_dates == visible
    assert ld_dates == sorted(ld_dates, reverse=True)


def test_order_by_push_sorts_descending_and_is_stable():
    fx = [{"id": "a", "_anchor": {"pushed_at": "2026-01-01T00:00:00Z"}},
          {"id": "b", "_anchor": {"pushed_at": "2026-03-01T00:00:00Z"}},
          {"id": "c", "_anchor": {"pushed_at": "2026-02-01T00:00:00Z"}}]
    assert [p["id"] for p in build.order_by_push(fx)] == ["b", "c", "a"]
    assert fx[1]["_pushed_date"] == "2026-03-01"


def test_missing_push_date_refuses_the_build():
    with pytest.raises(build.BuildRefused) as e:
        build.order_by_push([{"id": "x", "_anchor": {}}])
    assert e.value.reason == "PUSH_DATE_MISSING"
