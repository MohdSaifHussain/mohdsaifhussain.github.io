"""tools/fetch_stats.py — the anchor fetcher's own controls.

Added 2026-08-22 for DECISIONS CU-3. repo_names() had assumed every GitHub
link in projects.json was a repo root; the first deep links in the record
(a #fragment and a /blob/ path, both on switchyard) produced bogus repo names
and the fetcher died with KeyError: 'tag_name'. These tests were run against
the OLD code first and refused, so they are proven to detect that defect.
"""
from __future__ import annotations

import fetch_stats


def test_deep_links_map_to_their_repo_root_exactly_once():
    """Positive control: a root, a #fragment and a /blob/ path on the same repo
    yield that repo's name once, not three names."""
    data = {"projects": [{"links": {
        "repo": "https://github.com/MohdSaifHussain/switchyard",
        "see_it_running": "https://github.com/MohdSaifHussain/switchyard#see-it-running",
        "showcase": "https://github.com/MohdSaifHussain/switchyard/blob/main/docs/showcase/README.md",
    }}]}
    assert fetch_stats.repo_names(data) == ["switchyard"]


def test_non_github_links_produce_no_name():
    """Negative control: a GHCR or a pages link is not a repo and must not be
    fetched as one."""
    data = {"projects": [{"links": {
        "container": "https://ghcr.io/mohdsaifhussain/delivery-engine",
        "docs_site": "https://mohdsaifhussain.github.io/delivery-engine-fde-case-study/index.html",
    }}]}
    assert fetch_stats.repo_names(data) == []


def test_repo_root_with_trailing_slash_is_the_same_repo():
    assert fetch_stats.repo_name_from_link("https://github.com/MohdSaifHussain/OpsKit/") == "OpsKit"
    assert fetch_stats.repo_name_from_link("https://github.com/MohdSaifHussain/OpsKit#readme") == "OpsKit"
    assert fetch_stats.repo_name_from_link("https://example.com/MohdSaifHussain/OpsKit") is None
