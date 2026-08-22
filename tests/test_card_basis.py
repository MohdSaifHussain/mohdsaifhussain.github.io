"""P5.1 (STEP-10, defect D-60): each project card says how ITS figures were
obtained, chosen from the basis the entry declares, and the build refuses a
basis with no sentence. Until 2026-08-22 one hardcoded sentence was printed on
every card; it was true for one card of six.
"""
from __future__ import annotations

import json
import pathlib
import re

import pytest

import build

ROOT = pathlib.Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def site() -> pathlib.Path:
    assert build.build() == 0, "the real build must succeed"
    return build.OUT


def test_every_card_sentence_matches_its_declared_basis(site):
    """Positive control over the real data: one sentence per card, and the
    sentence on card N is the one for entry N's basis. Also proves every basis
    currently in use has a sentence, by covering them all."""
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    html = (site / "projects/index.html").read_text(encoding="utf-8")
    found = re.findall(r'<p class="mono-meta card-basis">(.*?)</p>', html, re.S)
    assert len(found) == len(data["projects"]), "one basis sentence per card"
    bases_seen = set()
    for entry, sentence in zip(data["projects"], found):
        expected = build.BASIS_SENTENCES[entry["metrics_basis"]]
        assert sentence.replace("&#39;", "'") == expected, entry["id"]
        bases_seen.add(entry["metrics_basis"])
    assert bases_seen == set(build.BASIS_SENTENCES), (
        "every defined sentence is exercised by at least one entry; a sentence "
        "nobody renders is the D-37 shape waiting to happen")


def test_unknown_basis_refused():
    with pytest.raises(build.BuildRefused) as e:
        build.attach_basis_sentences([{"id": "x", "metrics_basis": "vibes"}])
    assert e.value.reason == "BASIS_UNKNOWN"


def test_retired_basis_refused_with_its_own_reason():
    with pytest.raises(build.BuildRefused) as e:
        build.attach_basis_sentences([{"id": "x", "metrics_basis": "owner-measured"}])
    assert e.value.reason == "BASIS_RETIRED"


def test_no_em_dash_in_any_basis_sentence():
    """C-27 by hand-check scope (CU-2): the gate covers experience.json only."""
    for basis, sentence in build.BASIS_SENTENCES.items():
        assert "—" not in sentence, basis
