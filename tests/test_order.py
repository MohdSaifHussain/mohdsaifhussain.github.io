"""P5.5: entries render newest push first, everywhere, from the snapshot's
pushed_at, with the date shown as ISO 8601 in a <time datetime>. Positive
controls over the real build; negative controls over fixtures."""
from __future__ import annotations

import html as html_mod
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


def test_projects_page_is_newest_push_first_in_each_section(site):
    """P5.8: two sections, each ordered on its own; the case-studies section
    starts at its own h2, so the split point is that heading."""
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    html = (site / "projects/index.html").read_text(encoding="utf-8")
    top, cases = html.split('<h2 class="display-lg">Case studies</h2>')
    names_top = re.findall(r'<h2 class="display-md">(.*?)</h2>', top)
    names_cases = re.findall(r'<h2 class="display-md">(.*?)</h2>', cases)
    assert names_top == _expected([p for p in data["projects"] if not p.get("case_study")])
    assert names_cases == _expected([p for p in data["projects"] if p.get("case_study")])
    assert len(names_cases) == 2


def test_every_case_study_carries_its_outcome_and_source(site):
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    html = (site / "projects/index.html").read_text(encoding="utf-8")
    cases = [p for p in data["projects"] if p.get("case_study")]
    assert html.count("OUTCOME — FROM THE README") == len(cases)
    text = html_mod.unescape(html)   # Jinja escapes " as &#34; and ' as &#39;
    for p in cases:
        assert "outcome" in p and p["outcome"]["groups"], p["id"]
        assert "README" in p["outcome"]["source"], p["id"]
        for g in p["outcome"]["groups"]:
            for row in g["rows"]:
                assert row["k"] in text and row["v"] in text, (p["id"], row["k"])


def test_home_flagship_is_newest_push_first(site):
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    html = (site / "index.html").read_text(encoding="utf-8")
    names = re.findall(r'<span class="display-sm">(.*?)</span>', html)
    assert names == _expected([p for p in data["projects"] if p.get("flagship")])


def test_every_record_date_is_iso_8601(site):
    for page in ("projects/index.html", "index.html"):
        html = (site / page).read_text(encoding="utf-8")
        times = re.findall(r'<time class="pushed mono-meta" datetime="([^"]+)">(\d{4}-\d{2}-\d{2})</time>', html)
        assert times, page
        for instant, date in times:
            assert ISO_INSTANT.match(instant), instant
            assert instant.startswith(date)


def test_record_block_names_both_dcmi_terms_on_every_card(site):
    """P5.6: ISSUED and MODIFIED on every entry; a never-released repository
    says "no release yet" rather than borrowing the push date."""
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    html = (site / "projects/index.html").read_text(encoding="utf-8")
    assert html.count('<dt class="mono-label">Issued</dt>') == len(data["projects"])
    assert html.count('<dt class="mono-label">Modified</dt>') == len(data["projects"])
    snap = _snapshot()
    never = [n for n, r in snap.items() if r.get("anchor_type") == "commit"
             and any(p["links"]["repo"].endswith("/" + n) for p in data["projects"])]
    assert html.count("no release yet") == len(never)


def test_jsonld_published_matches_issued(site):
    html = (site / "projects/index.html").read_text(encoding="utf-8")
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
    snap = _snapshot()
    for item in ld["itemListElement"]:
        name = item["item"]["codeRepository"].rstrip("/").rsplit("/", 1)[-1]
        issued = snap[name]["issued_at"]
        assert item["item"].get("datePublished") == (issued if issued else None)


def test_snapshot_without_issued_key_refuses():
    with pytest.raises(build.BuildRefused) as e:
        build.order_by_push([{"id": "x", "_anchor": {"pushed_at": "2026-01-01T00:00:00Z"}}])
    assert e.value.reason == "ISSUED_DATE_MISSING"


def test_jsonld_date_matches_the_visible_one(site):
    html = (site / "projects/index.html").read_text(encoding="utf-8")
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
    ld_dates = [i["item"]["dateModified"] for i in ld["itemListElement"]]
    visible = re.findall(r'<dt class="mono-label">Modified</dt>\s*<dd><time class="pushed mono-meta" datetime="([^"]+)"', html)
    assert ld_dates == visible
    assert ld_dates == sorted(ld_dates, reverse=True)


def test_order_by_push_sorts_descending_and_is_stable():
    fx = [{"id": "a", "_anchor": {"pushed_at": "2026-01-01T00:00:00Z", "issued_at": None}},
          {"id": "b", "_anchor": {"pushed_at": "2026-03-01T00:00:00Z", "issued_at": "2026-02-28T00:00:00Z"}},
          {"id": "c", "_anchor": {"pushed_at": "2026-02-01T00:00:00Z", "issued_at": None}}]
    assert [p["id"] for p in build.order_by_push(fx)] == ["b", "c", "a"]
    assert fx[1]["_pushed_date"] == "2026-03-01"


def test_missing_push_date_refuses_the_build():
    with pytest.raises(build.BuildRefused) as e:
        build.order_by_push([{"id": "x", "_anchor": {}}])
    assert e.value.reason == "PUSH_DATE_MISSING"
