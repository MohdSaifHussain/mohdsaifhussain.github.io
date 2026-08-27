"""P5.4: the architecture diagrams are generated, not hand-edited, and no text
in any of them may overlap a node or another text. Both facts are guarded here
so a drawing cannot drift from its generator and a collision cannot ship."""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import gen_diagrams  # noqa: E402


def test_every_diagram_is_collision_free():
    for make in gen_diagrams.DIAGRAMS:
        d = make()
        assert d.check() == [], d.name


def test_committed_diagrams_match_their_generator():
    """A hand edit to an .svg.j2 would bypass the overlap check; the committed
    file must be byte-identical to what the generator produces."""
    for make in gen_diagrams.DIAGRAMS:
        d = make()
        committed = (ROOT / "templates/diagrams" / f"{d.name}.svg.j2").read_text(encoding="utf-8")
        assert committed == d.svg(), f"{d.name}: run python tools/gen_diagrams.py"


def test_every_declared_diagram_exists_and_is_cited():
    data = json.loads((ROOT / "data/projects.json").read_text(encoding="utf-8"))
    names = {make().name for make in gen_diagrams.DIAGRAMS}
    for p in data["projects"]:
        if "diagram" in p:
            assert p["diagram"] in names, p["id"]
            assert (ROOT / "templates/diagrams" / f"{p['diagram']}.svg.j2").exists()
            assert "README" in p.get("diagram_source", ""), f"{p['id']}: cite the README lines"


def test_overlap_checker_refuses_a_collision():
    """Negative control: a label placed on a node must trip the checker."""
    d = gen_diagrams.Diagram("x", "x", 400, 200)
    d.node("a", 0, 50, ["alpha"], w=100); d.node("b", 200, 50, ["beta"], w=100)
    d.emit_node("a"); d.emit_node("b")
    d.edge("a", "b", "a label that sits on beta", label_at=(250, 70))
    assert any("overlaps" in p for p in d.check())
