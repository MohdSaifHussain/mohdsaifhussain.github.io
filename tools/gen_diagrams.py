"""Generate the inline SVG architecture diagrams under templates/diagrams/.

Each diagram is transcribed from the project's own README (the mermaid
flowchart or the section named in `SOURCE`): node labels are the README's text,
geometry is this site's own. Run after editing the specs below:

    python tools\\gen_diagrams.py

The generator refuses to write a diagram in which any text box overlaps a node
or another text box (REASON=DIAGRAM_OVERLAP), so a label can never start in one
box and end in the next. Widths are estimated from IBM Plex Mono's advance
(0.6em) with a margin, which is conservative rather than exact.

Edges are straight <line>s so the site's motion rule holds: they are drawn by
`transform: scale()` from their start point (C-15: transform/opacity only).
"""
from __future__ import annotations

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "templates" / "diagrams"

LABEL_PX = 11      # .d-label   (--type-mono-meta-sm)
EYEBROW_PX = 10    # .d-eyebrow (--type-mono-label, letter-spaced)
CHAR = 0.62        # advance per character, em, with a little margin
LH = 13            # line height inside a node


def text_w(s: str, px: int, spaced: bool = False) -> float:
    return len(s) * px * (CHAR + (0.08 if spaced else 0))


class Diagram:
    def __init__(self, name: str, title: str, width: int, height: int):
        self.name, self.title, self.w, self.h = name, title, width, height
        self.nodes: dict[str, dict] = {}
        self.items: list[str] = []      # DOM order = posting order
        self.boxes: list[tuple[float, float, float, float, str]] = []  # collision set

    # ---- geometry helpers -------------------------------------------------
    def node(self, i, x, y, lines, kind="box", w=None, h=None, anchor=None):
        lines = list(lines)
        w = w or max(text_w(l, LABEL_PX) for l in lines) + 24
        h = h or len(lines) * LH + 16
        if kind == "diamond":
            w += 40; h += 22
        self.nodes[i] = dict(x=x, y=y, w=w, h=h, lines=lines, kind=kind)
        self.boxes.append((x, y, x + w, y + h, f"node {i}"))
        return self

    def n(self, i): return self.nodes[i]
    def cx(self, i): d = self.n(i); return d["x"] + d["w"] / 2
    def cy(self, i): d = self.n(i); return d["y"] + d["h"] / 2
    def left(self, i):   d = self.n(i); return d["x"], self.cy(i)
    def right(self, i):  d = self.n(i); return d["x"] + d["w"], self.cy(i)
    def top(self, i):    d = self.n(i); return self.cx(i), d["y"]
    def bottom(self, i): d = self.n(i); return self.cx(i), d["y"] + d["h"]

    # ---- emitters -----------------------------------------------------------
    def eyebrow(self, x, y, text, accent=False):
        cls = "d-eyebrow d-eyebrow--accent" if accent else "d-eyebrow"
        self.items.append(f'<g class="d-item d-region"><text class="{cls}" x="{x}" y="{y}">{esc(text)}</text></g>')
        w = text_w(text, EYEBROW_PX, spaced=True)
        self.boxes.append((x, y - EYEBROW_PX, x + w, y + 3, f"eyebrow '{text[:24]}'"))

    def region(self, x, y, w, h, text, accent=False):
        cls = "d-eyebrow d-eyebrow--accent" if accent else "d-eyebrow"
        self.items.append(f'<g class="d-item d-region"><rect class="d-boundary" x="{x}" y="{y}" width="{w}" height="{h}" rx="2"/>'
                          f'<text class="{cls}" x="{x + 12}" y="{y + 16}">{esc(text)}</text></g>')
        tw = text_w(text, EYEBROW_PX, spaced=True)
        self.boxes.append((x + 12, y + 6, x + 12 + tw, y + 19, f"region '{text[:24]}'"))

    def emit_node(self, i):
        d = self.n(i); x, y, w, h, lines, kind = d["x"], d["y"], d["w"], d["h"], d["lines"], d["kind"]
        cx, cy = self.cx(i), self.cy(i)
        g = [f'<g class="d-item d-node d-node--{kind}">']
        if kind == "diamond":
            g.append(f'<polygon class="d-shape" points="{cx:.0f},{y:.0f} {x + w:.0f},{cy:.0f} {cx:.0f},{y + h:.0f} {x:.0f},{cy:.0f}"/>')
        else:
            rx = 8 if kind == "store" else 1
            g.append(f'<rect class="d-shape" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{rx}"/>')
        y0 = cy - (len(lines) - 1) * LH / 2 + 4
        for k, line in enumerate(lines):
            g.append(f'<text class="d-label" x="{cx:.0f}" y="{y0 + k * LH:.0f}" text-anchor="middle">{esc(line)}</text>')
        g.append("</g>")
        self.items.append("".join(g))

    def edge(self, a, b, label="", dashed=False, at=None, label_at=None, kind=None):
        """a, b: node ids or explicit (x, y) points. `at` picks the ports:
        ('right','left') etc. label_at: explicit (x, y) for the label, else
        just above the midpoint. Labels are collision-checked like nodes."""
        (x1, y1), (x2, y2) = self._ports(a, b, at)
        cls = "d-item d-edge" + (" d-edge--dashed" if dashed else "") + (f" d-edge--{kind}" if kind else "")
        if y2 < y1:
            cls += " d-edge--up"
        if x2 < x1:
            cls += " d-edge--back"
        e = [f'<g class="{cls}"><line class="d-line" x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}"/>']
        if label:
            lx, ly = label_at or ((x1 + x2) / 2, (y1 + y2) / 2 - 6)
            e.append(f'<text class="d-edge-label" x="{lx:.0f}" y="{ly:.0f}" text-anchor="middle">{esc(label)}</text>')
            tw = text_w(label, EYEBROW_PX)
            self.boxes.append((lx - tw / 2, ly - EYEBROW_PX, lx + tw / 2, ly + 3, f"label '{label[:28]}'"))
        e.append("</g>")
        self.items.append("".join(e))

    def _ports(self, a, b, at):
        if at is None:
            at = ("right", "left")
        pa = a if isinstance(a, tuple) else getattr(self, at[0])(a)
        pb = b if isinstance(b, tuple) else getattr(self, at[1])(b)
        return pa, pb

    # ---- output -------------------------------------------------------------
    def check(self) -> list[str]:
        out = []
        for i, (ax1, ay1, ax2, ay2, an) in enumerate(self.boxes):
            for bx1, by1, bx2, by2, bn in self.boxes[i + 1:]:
                if an.startswith("region") or bn.startswith("region"):
                    pass
                if ax1 < bx2 and bx1 < ax2 and ay1 < by2 and by1 < ay2:
                    # a node sitting INSIDE a region rectangle is by design;
                    # only text/eyebrow strips and nodes are compared here.
                    out.append(f"{self.name}: {an} overlaps {bn}")
            if ax2 > self.w or ay2 > self.h or ax1 < 0 or ay1 < 0:
                out.append(f"{self.name}: {an} leaves the {self.w}x{self.h} canvas")
        return out

    def svg(self) -> str:
        head = (f'<svg class="diagram" data-post viewBox="0 0 {self.w} {self.h}" role="img" '
                f'aria-labelledby="{self.name}-diagram-title" xmlns="http://www.w3.org/2000/svg">\n'
                f'<title id="{self.name}-diagram-title">{esc(self.title)}</title>\n')
        return head + "\n".join(self.items) + "\n</svg>\n"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# =============================================================================
# The diagrams. SOURCE names the README lines each is transcribed from.
# =============================================================================

def finding_bridge() -> Diagram:
    # SOURCE: README.md:63-99 (mermaid flowchart), origin/master 41a33ed
    d = Diagram("finding-bridge", "finding-bridge architecture: sources, a deterministic core with a sealing boundary and a human gate, and destinations", 1200, 400)
    d.eyebrow(0, 14, "SOURCES")
    d.eyebrow(200, 14, "DETERMINISTIC CORE: NO AI, NO API KEY")
    d.eyebrow(1000, 134, "DESTINATIONS")
    d.node("G", 0, 30, ["garak hitlog JSONL"], w=150)
    d.node("T", 0, 92, ["attack transcript,", "text or JSON"], w=150)
    d.node("I", 200, 53, ["ingest"], w=100)
    d.node("P", 350, 53, ["safe metadata", "preview"], w=150)
    d.node("H", 550, 53, ["stamp: RFC 8785", "hash and chain"], w=170)
    d.node("D", 770, 53, ["dedup,", "exact match"], w=130)
    d.node("C", 950, 40, ["human gate:", "confirm or reject"], "diamond", w=110, h=60)
    d.node("L", 1100, 53, ["ledger and head"], "store", w=100, h=42)
    d.region(185, 215, 440, 130, "SEALING BOUNDARY: RAW CONTENT ENCRYPTED AT REST", accent=True)
    d.node("S", 200, 245, ["sealed store,", "Fernet blobs"], "store", w=150)
    d.node("X", 460, 245, ["exposure log,", "append-only"], "store", w=150)
    d.node("AI", 660, 245, ["caged --ai: prose suggestions", "only, off by default"], "dashed")
    for k, (i, label) in enumerate([("M", "Markdown packet"), ("SA", "SARIF 2.1.0"), ("TR", "tracker JSON"), ("F", "FLARE-AI, provisional")]):
        d.node(i, 1000, 150 + k * 50, [label], w=200, h=30)
    for i in ("G", "T"):
        d.emit_node(i)
    d.emit_node("I"); d.edge("G", "I"); d.edge("T", "I")
    d.emit_node("P"); d.edge("I", "P")
    d.emit_node("H"); d.edge("P", "H")
    d.emit_node("D"); d.edge("H", "D")
    d.emit_node("C"); d.edge("D", "C")
    d.emit_node("L"); d.edge("C", "L")
    lx, ly = d.bottom("L")
    for i in ("M", "SA", "TR", "F"):
        d.emit_node(i); d.edge((lx, ly), i)
    d.emit_node("S"); d.edge("I", "S", "raw content", at=("bottom", "top"), label_at=(250, 170))
    d.emit_node("X"); d.edge("S", "X", "unseal --explicit, every read logged", dashed=True, label_at=(405, 320))
    d.emit_node("AI"); d.edge("AI", "C", "reads the preview, never sealed content", dashed=True, at=("top", "bottom"), label_at=(840, 200))
    return d


def ts_sentry() -> Diagram:
    # SOURCE: README.md:29-47 (mermaid flowchart), origin/main 977d520
    d = Diagram("ts-sentry", "TS-Sentry control path: an agent proposes, the input firewall and mandate check bound it, the consequence gate and hash-chained ledger record it, and only an analyst can enforce", 1200, 330)
    d.node("A", 0, 53, ["Agent", "proposes"], w=110)
    d.node("F", 160, 53, ["Input firewall", "content is inert data"])
    d.node("V", 390, 40, ["Mandate check", "before dispatch"], "diamond", h=60)
    d.node("G", 620, 40, ["Consequence gate", "OBSERVE / ASSEMBLE / RECOMMEND"], "diamond", h=60)
    d.node("L", 960, 53, ["Hash-chained ledger"], "store", h=42)
    d.node("H", 960, 180, ["Analyst signs", "the only route to ENFORCE"], "gate")
    d.node("R", 390, 190, ["Never executed", "and ledgered"])
    d.node("RJ", 650, 190, ["GATE_REJECTION"])
    d.node("X", 0, 240, ["ENFORCE", "unreachable by any agent,", "at type level"], "danger")
    d.emit_node("A"); d.emit_node("F"); d.edge("A", "F")
    d.emit_node("V"); d.edge("F", "V")
    d.emit_node("G"); d.edge("V", "G", "inside", label_at=(588, 60))
    d.emit_node("L"); d.edge("G", "L", "passes", label_at=(924, 60))
    d.emit_node("R"); d.edge("V", "R", "outside", at=("bottom", "top"), label_at=(505, 155))
    d.emit_node("RJ"); d.edge("G", "RJ", "fails", at=("bottom", "top"), label_at=(760, 155))
    d.edge("R", "L", at=("right", "bottom"))
    d.edge("RJ", "L", at=("right", "bottom"))
    d.emit_node("H"); d.edge("L", "H", at=("bottom", "top"))
    d.emit_node("X")
    return d


def delivery_engine() -> Diagram:
    # SOURCE: README.md:57-82 (mermaid flowchart TD), origin/main 4d40293
    d = Diagram("delivery-engine", "Delivery Engine architecture: a user goal and dataset enter the planner, pass Human Gate 1, run through the executor's stage contract, and leave as a hashed package", 1200, 470)
    d.node("A", 0, 200, ["User goal", "+ dataset"], w=120)
    d.region(170, 150, 330, 175, "PLANNER")
    d.node("B1", 185, 185, ["80% deterministic classification,", "20% LLM (ambiguity only)"])
    d.node("B2", 185, 255, ["Human Gate 1: plan approved", "before execution"], "gate")
    d.region(550, 10, 420, 450, "EXECUTOR: STAGE CONTRACT")
    d.node("C0", 565, 40, ["declared inputs, execution, output hashed,", "gate evaluated, audit entry, next stage"])
    d.node("C1", 565, 105, ["KIT stages: AnalystKit (profile, validate,", "dedupe) and OpsKit (weekly-review, drill)", "via MCP servers, findings sealed into the store"])
    d.node("C2", 565, 182, ["AI stages: prose and structure only,", "every number injected from the store.", "Human Gate 2: AI-drafted rules approved by hash"], "gate")
    d.node("C3", 565, 259, ["MODEL stage: deterministic fixed-seed", "baseline; metrics hashed; no AI-generated code"])
    d.node("C4", 565, 323, ["STATS stage: deterministic inference,", "alpha pre-registered; significance never gates"])
    d.node("C5", 565, 387, ["MATH stage: deterministic shape,", "MAD outliers, distribution fits, entropy, temporal"])
    d.node("D", 1010, 200, ["PACKAGE: notebook, reports,", "PPT, DQ workpaper, README,", "audit log, manifest (hash tree)"], "store", w=190)
    d.emit_node("A")
    d.emit_node("B1"); d.edge("A", "B1")
    d.emit_node("B2"); d.edge("B1", "B2", at=("bottom", "top"))
    d.emit_node("C0"); d.edge((500, 237), (550, 237))
    for i in ("C1", "C2", "C3", "C4", "C5"):
        d.emit_node(i)
    d.emit_node("D"); d.edge((970, 237), "D")
    return d


def switchyard() -> Diagram:
    # SOURCE: docs/showcase/README.md:18-43 (mermaid flowchart TB), origin/main 560c107
    d = Diagram("switchyard", "Switchyard topology: clients reach the gateway pod in a kind cluster reconciled by Argo CD; the gateway and worker share Redis, Ollama and the OpenTelemetry collector", 1200, 430)
    d.node("client", 0, 120, ["Client", "OpenAI-format requests"])
    d.region(260, 20, 360, 300, "KIND KUBERNETES CLUSTER: HELM CHART, RECONCILED BY ARGO CD")
    d.node("gw", 290, 60, ["Gateway pod", "routing, fallback, quotas,", "cost, tracing"])
    d.node("worker", 290, 210, ["Worker pod", "async jobs, same provider path"])
    d.node("redis", 700, 130, ["Redis", "quotas, cost records, job streams"], "store")
    d.node("ollama", 990, 60, ["Ollama on the host", "qwen3:4b, llama3.2:1b"], "store", h=44)
    d.node("otel", 990, 230, ["OpenTelemetry Collector", "to Prometheus, to Grafana"])
    d.node("git", 0, 350, ["This Git repository", "Helm chart on main"], "store")
    d.node("argo", 320, 350, ["Argo CD"], w=120)
    d.emit_node("client")
    d.emit_node("gw"); d.edge("client", "gw", "POST /v1/chat/completions, /v1/jobs", label_at=(150, 100))
    d.emit_node("ollama"); d.edge("gw", "ollama", "forwards completion", at=("right", "left"), label_at=(760, 70))
    d.emit_node("redis"); d.edge("gw", "redis", "read quota, write cost, submit job", at=("right", "left"), label_at=(590, 130))
    d.emit_node("worker"); d.edge("redis", "worker", "consumer group delivers the job", at=("left", "right"), label_at=(615, 205))
    d.edge("worker", "ollama", "routes and generates", at=("right", "bottom"), label_at=(870, 210))
    d.emit_node("otel"); d.edge("gw", "otel", at=("bottom", "left")); d.edge("worker", "otel", "gen_ai spans, metrics", at=("right", "left"), label_at=(830, 270))
    d.emit_node("git"); d.emit_node("argo"); d.edge("git", "argo", "GitOps source of truth", label_at=(237, 360))
    d.edge("argo", (440, 320), "reconciles / self-heals", at=("top", "top"), label_at=(520, 345))
    return d


def analystkit() -> Diagram:
    # SOURCE: README.md:185-208 (Security architecture), origin/main 3a516af
    d = Diagram("analystkit", "AnalystKit security architecture: three stacked injection defences in front of a deterministic engine, an audit boundary of SHA-256 hashed findings, and an optional AI layer that never touches data", 1200, 330)
    d.eyebrow(0, 14, "THREE STACKED INJECTION DEFENCES")
    d.node("src", 0, 100, ["Source data"], w=110)
    d.node("d1", 160, 40, ["READ_ONLY attach:", "even a successful injection", "cannot write"])
    d.node("d2", 160, 120, ["Prepared-statement parameter", "binding: values can never", "become SQL"])
    d.node("d3", 160, 200, ["Validate-then-quote identifiers:", "names can never become SQL"])
    d.node("eng", 470, 100, ["deterministic", "engine first"], w=140)
    d.region(650, 60, 260, 120, "AUDIT BOUNDARY", accent=True)
    d.node("hash", 665, 100, ["findings hashed", "to SHA-256"], "store", w=230)
    d.node("model", 940, 100, ["only the hash and findings", "JSON reach the model"], "dashed")
    d.node("narr", 940, 220, ["narrative labeled: verify against", "the deterministic findings above"])
    d.node("never", 470, 220, ["AI never writes SQL, queries data,", "or produces a number"], "dashed")
    d.emit_node("src")
    for i in ("d1", "d2", "d3"):
        d.emit_node(i); d.edge("src", i, at=("right", "left"))
    d.emit_node("eng")
    for i in ("d1", "d2", "d3"):
        d.edge(i, "eng", at=("right", "left"))
    d.emit_node("hash"); d.edge("eng", "hash")
    d.emit_node("model"); d.edge("hash", "model")
    d.emit_node("narr"); d.edge("model", "narr", at=("bottom", "top"))
    d.emit_node("never")
    return d


def opskit() -> Diagram:
    # SOURCE: README.md:130-171 (The sequence; The conditional drill-down), origin/main 959b352
    d = Diagram("opskit", "OpsKit: playbooks run the SHAPE, TRUST, CHANGE, DRIVER, CONCENTRATION, ACTION sequence, and the driver step is a conditional drill-down where each level is computed inside its parent", 1200, 360)
    d.eyebrow(0, 14, "PLAYBOOKS")
    d.node("p1", 0, 30, ["weekly-review"], w=170)
    d.node("p2", 0, 78, ["data-quality"], w=170)
    d.node("p3", 0, 126, ["trend-investigation"], w=170)
    d.node("p4", 0, 174, ["Custom (TOML)"], "dashed", w=170)
    d.eyebrow(260, 14, "THE SEQUENCE")
    steps = ["SHAPE", "TRUST", "CHANGE", "DRIVER", "CONCENTRATION", "ACTION"]
    x = 260
    for s in steps:
        w = text_w(s, LABEL_PX) + 30
        d.node(s, x, 95, [s], "gate" if s == "DRIVER" else "box", w=w)
        x += w + 40
    d.region(430, 200, 640, 145, "THE CONDITIONAL DRILL-DOWN: EACH LEVEL COMPUTED INSIDE ITS PARENT")
    d.node("l1", 445, 235, ["service='payments' explains 84%", "of the change (312 to 578)"])
    d.node("l2", 750, 235, ["within that, severity='P2' explains", "67% (198 to 412)"])
    for i in ("p1", "p2", "p3", "p4"):
        d.emit_node(i)
    prev = None
    for s in steps:
        d.emit_node(s)
        if prev:
            d.edge(prev, s)
        else:
            for i in ("p1", "p2", "p3", "p4"):
                d.edge(i, s, at=("right", "left"))
        prev = s
    d.emit_node("l1"); d.edge("DRIVER", "l1", at=("bottom", "top"))
    d.emit_node("l2"); d.edge("l1", "l2", "condition on it, then find the next", label_at=(595, 315))
    return d


DIAGRAMS = [finding_bridge, ts_sentry, delivery_engine, switchyard, analystkit, opskit]


def main() -> int:
    OUT.mkdir(exist_ok=True)
    problems = []
    for make in DIAGRAMS:
        d = make()
        problems += d.check()
        if not problems:
            (OUT / f"{d.name}.svg.j2").write_text(d.svg(), encoding="utf-8", newline="\n")
            print(f"  wrote {d.name:18s} {len(d.nodes):2d} nodes  {len(d.items):2d} items  {d.w}x{d.h}")
    if problems:
        print("DIAGRAM CHECK FAILED")
        for p in problems:
            print(f"  REASON=DIAGRAM_OVERLAP  {p}")
        return 1
    print("DIAGRAMS OK: no text box overlaps a node or another text box")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
