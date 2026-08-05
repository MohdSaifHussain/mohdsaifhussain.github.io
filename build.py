"""Deterministic static build: data/*.json + templates -> _site/.  P3.1 / D2.

Charter C-34 (single source of truth: every page generated from structured data,
no content hand-duplicated), C-18 (no inline script), contract 3.2/3.3/3.6/3.7.

Every gate below has a distinct REASON code and is a pure function over text, so
tools can poison it directly. `--selftest` proves each one can fail AND that the
real inputs do not trip it — a gate that refuses everything looks identical to a
gate that works, until you check (doctrine rule 5).

Usage (PowerShell):
    python build.py
    python build.py --selftest
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")     # defect D-13: cp1252 console
sys.stderr.reconfigure(encoding="utf-8")

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound  # noqa: E402
from markupsafe import Markup  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
TPL = ROOT / "templates"
STATIC = ROOT / "static"
ASSETS = ROOT / "assets"
OUT = ROOT / "_site"

DATA_FILES = ["profile", "projects", "experience", "certifications"]

BASE_URL = "https://mohdsaifhussain.github.io"

# --- Content Security Policy (C-18).  P3.4 / D1. -------------------------
# Held as structured data rather than a string literal so it can be asserted
# against directive by directive.
#
# DELIVERED VIA <meta>, because GitHub Pages serves no custom response headers
# (charter §7). Verified against CSP Level 3 §3.3 on 2026-08-06:
#   "Neither are the report-uri, frame-ancestors, and sandbox directives."
#   "The Content-Security-Policy-Report-Only header is not supported inside a
#    meta element."
#   https://www.w3.org/TR/CSP3/
#
# Two consequences, both declared on /audit rather than papered over:
#  1. `frame-ancestors` CANNOT be set here. It is the modern replacement for
#     X-Frame-Options, so this platform offers NO clickjacking control at all —
#     a wider gap than A4.1 originally described. It is deliberately ABSENT
#     below: writing a directive the spec says is ignored would look like
#     protection while providing none.
#  2. There is no report-only mode via meta, so no staged rollout is possible.
#     The policy is enforced from the first deploy, which is why D2 verifies it
#     with captured console output from the published site.
CSP = {
    "default-src": "'self'",
    "script-src": "'self'",      # no 'unsafe-inline', no 'unsafe-eval'
    "style-src": "'self'",       # earned by the zero-inline-style gate since P3.1
    "img-src": "'self'",
    "font-src": "'self'",
    "manifest-src": "'self'",
    "connect-src": "'none'",     # nothing fetches; a future beacon would break loudly
    "object-src": "'none'",
    "frame-src": "'none'",
    "base-uri": "'none'",
    "form-action": "'none'",     # the site has no forms (charter §2)
}


def csp_value() -> str:
    return "; ".join(f"{k} {v}" for k, v in CSP.items())

# (template, output path, nav id, title, url path, description)
# Titles follow R-07: every page title matches its nav label. Descriptions are
# SEO metadata rather than portfolio content, so they live here on the R-03
# precedent; the counts inside them are still interpolated from data, never
# typed. Recorded as reading R-12.
PAGES = [
    ("index.html.j2", "index.html", "index", "Home", "/",
     "{headline}. Governed, audited systems where every claim is traceable."),
    ("projects.html.j2", "projects/index.html", "projects", "Projects", "/projects/",
     "{n_projects} engineering case studies, each with its method, its verified "
     "metrics and a version anchor linking back to the source repository."),
    ("experience.html.j2", "experience/index.html", "experience", "Experience", "/experience/",
     "{n_roles} roles across {years} years in operations, technical escalation, "
     "data quality and AI operations. Web resume available as PDF."),
    ("certifications.html.j2", "certifications/index.html", "certifications",
     "Certifications", "/certifications/",
     "Certifications and completed courses. Entries appear only when completed "
     "and publicly verifiable."),
    ("audit.html.j2", "audit/index.html", "audit", "Audit", "/audit/",
     "This site's own report card: measured standards, charter checks, the "
     "complete list of shipped animations, and its declared limitations."),
]

NAV = [
    # R-10, owner-directed: "01 INDEX" -> "01 HOME". Every label names its page
    # plainly; navigation clarity outranks ledger voice at the wayfinding layer.
    {"id": "index",          "label": "01 HOME",           "href": "/"},
    {"id": "projects",       "label": "02 PROJECTS",       "href": "/projects/"},
    {"id": "experience",     "label": "03 EXPERIENCE",     "href": "/experience/"},
    {"id": "certifications", "label": "04 CERTIFICATIONS", "href": "/certifications/"},
    {"id": "audit",          "label": "A / AUDIT",         "href": "/audit/"},
]

# Charter §5 fixes this sentence verbatim; it is site chrome mandated by the
# charter rather than portfolio content, so it is NOT in data/*.json. Recorded
# as reading R-03 — C-34 governs portfolio content, and putting charter text
# into an owner-verified data file would need re-verification (O-3) to no gain.
COLOPHON = ("An AI-orchestrated portfolio: designed and built by Mohd Saif "
            "Hussain directing Claude, under a governed, audited process.")

# Decision D-03: v1.0.0 ships zero third-party resources, so the counter is an
# honest dash. Flipping this to a real counter is a one-line change here.
VISITS = "—"


class BuildRefused(Exception):
    def __init__(self, reason: str, detail: str):
        super().__init__(f"REASON={reason}  {detail}")
        self.reason, self.detail = reason, detail


# ---------------------------------------------------------------- gates ----
# Each returns a list of (REASON, detail). Pure over text: poisonable.

# Defect D-19: a numeric HTML entity (&#8599; for ↗) is indistinguishable from
# a 4-digit hex colour by shape alone, so the gate false-refused valid markup.
# The negative lookbehind on & is the discriminator. A gate that refuses valid
# input is as broken as one that accepts invalid input — it just fails loudly.
HEX = re.compile(r"(?<!&)#[0-9a-fA-F]{3,8}\b")
RGB = re.compile(r"\brgba?\s*\(")
VAR_USE = re.compile(r"var\(\s*(--[\w-]+)")
VAR_DEF = re.compile(r"^\s*(--[\w-]+)\s*:", re.M)
MARK_SVG = re.compile(r'<svg[^>]*class="mark\b[^>]*>')
VIEWBOX = re.compile(r'viewBox="([^"]+)"')
STROKE_W = re.compile(r'stroke-width="([^"]+)"')
INLINE_STYLE_ATTR = re.compile(r"<[^>]+\sstyle\s*=", re.I)
# An inline <script> with EXECUTABLE content. A data block is not executable
# and is explicitly excluded, on the authority of the HTML standard rather than
# from memory: in "prepare the script element"
# (https://html.spec.whatwg.org/multipage/scripting.html), an unrecognised type
# returns at step 13 — "No script is executed, and el's type is left as null" —
# whereas the "Should element's inline behavior be blocked by Content Security
# Policy?" check is step 21. A data block never reaches the CSP check, so
# application/ld+json is safe under a strict script-src with no 'unsafe-inline'.
# Verified against the spec 2026-08-06; P3.4 confirms it on a live console.
DATA_BLOCK_TYPES = ("application/ld+json",)
INLINE_SCRIPT = re.compile(
    r"<script(?![^>]*\bsrc=)(?![^>]*\btype=[\"'](?:" +
    "|".join(re.escape(t) for t in DATA_BLOCK_TYPES) + r")[\"'])[^>]*>\s*\S", re.I)


def gate_color_literal(text: str, where: str) -> list[tuple[str, str]]:
    """Contract 3.2 — no colour literal outside tokens.css."""
    out = []
    for m in HEX.finditer(text):
        out.append(("COLOR_LITERAL", f"{where}: hex {m.group()}"))
    for m in RGB.finditer(text):
        out.append(("COLOR_LITERAL", f"{where}: {m.group().strip()}...)"))
    return out


def gate_unknown_token(css: str, defined: set[str], where: str) -> list[tuple[str, str]]:
    """Contract 3.2 — every var() resolves to a token defined in tokens.css."""
    return [("TOKEN_UNKNOWN", f"{where}: {name} is not defined in tokens.css")
            for name in sorted({m.group(1) for m in VAR_USE.finditer(css)} - defined)]


def gate_inline(html: str, where: str) -> list[tuple[str, str]]:
    """Contract 3.3 / C-18 — no inline style attribute, no inline script body."""
    out = []
    if INLINE_STYLE_ATTR.search(html):
        out.append(("INLINE_STYLE", f"{where}: a style= attribute reached the output"))
    if INLINE_SCRIPT.search(html):
        out.append(("INLINE_SCRIPT", f"{where}: an inline <script> body reached the output"))
    return out


def gate_mark_drift(html: str, where: str) -> list[tuple[str, str]]:
    """D-14's added condition — every mark resolves from the ONE shared
    definition, so no future edit can restyle one mark without the other."""
    svgs = MARK_SVG.findall(html)
    if not svgs:
        return []
    boxes = {m.group(1) for s in svgs if (m := VIEWBOX.search(s))}
    if len(boxes) > 1:
        return [("MARK_DRIFT", f"{where}: marks disagree on viewBox: {sorted(boxes)}")]
    return []


def gate_mark_drift_paths(html: str, where: str) -> list[tuple[str, str]]:
    """Same condition, checked on the stroke the paths actually carry."""
    widths = set()
    for m in re.finditer(r'<svg[^>]*class="mark\b.*?</svg>', html, re.S):
        widths |= {w.group(1) for w in STROKE_W.finditer(m.group())}
    if len(widths) > 1:
        return [("MARK_DRIFT", f"{where}: marks disagree on stroke-width: {sorted(widths)}")]
    return []


def gate_mark_source(macros_src: str, other_srcs: dict[str, str]) -> list[tuple[str, str]]:
    """D-14's added condition, at the source level: exactly one place in the
    whole template tree may emit a mark <svg>, and it is _mark()."""
    out = []
    n = len(MARK_SVG.findall(macros_src))
    if n != 1:
        out.append(("MARK_SOURCE",
                    f"_macros.html.j2 emits {n} mark <svg> elements; the shared "
                    f"definition requires exactly 1 (_mark)"))
    for name, src in sorted(other_srcs.items()):
        if MARK_SVG.search(src):
            out.append(("MARK_SOURCE", f"{name} emits a mark <svg> directly; it must call _mark via mark_check/mark_cross"))
    return out


# ----------------------------------------------------------------- load ----

def load_data(data_dir: pathlib.Path | None = None) -> dict:
    data_dir = DATA if data_dir is None else data_dir
    data = {}
    for name in DATA_FILES:
        path = data_dir / f"{name}.json"
        shown = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        if not path.exists():
            raise BuildRefused("DATA_MISSING", f"{shown} not found")
        try:
            data[name] = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise BuildRefused("DATA_MALFORMED", f"{shown}: {e}") from e
    return data


def gate_anchors(projects: list[dict], snapshot: dict) -> list[tuple[str, str]]:
    """Contract 3.3 — every project's figures must be able to render BOTH a
    version anchor and an evidence link. A bare number is a claim without a
    source, which is what defect D-02 was about.
    """
    out = []
    repos = snapshot.get("repos", {})
    for p in projects:
        repo_url = (p.get("links") or {}).get("repo", "")
        name = repo_url.rstrip("/").rsplit("/", 1)[-1] if repo_url else ""
        if not name:
            out.append(("STAT_UNANCHORED", f"{p['id']}: no repo link, nothing to anchor to"))
        elif name not in repos:
            out.append(("STAT_UNANCHORED", f"{p['id']}: '{name}' absent from the snapshot"))
        elif not repos[name].get("anchor") or not repos[name].get("anchor_url"):
            out.append(("STAT_UNANCHORED", f"{p['id']}: anchor or evidence link missing"))
    return out


def read_token(tokens_css: str, name: str) -> str:
    m = re.search(rf"^\s*{re.escape(name)}:\s*(#[0-9a-fA-F]{{3,8}})\s*;", tokens_css, re.M)
    if not m:
        raise BuildRefused("TOKEN_UNKNOWN", f"{name} is not defined in tokens.css")
    return m.group(1)


def load_snapshot() -> dict:
    """The committed GitHub snapshot. build.py never fetches (contract 3.2)."""
    path = DATA / "generated" / "github.json"
    if not path.exists():
        raise BuildRefused(
            "SNAPSHOT_MISSING",
            f"{path.relative_to(ROOT)} not found  (run: python tools\\fetch_stats.py)")
    snap = json.loads(path.read_text(encoding="utf-8"))

    # Q2 ruling: staleness NEVER fails the build. Warn in build output only;
    # the page carries its honest "as of" date regardless.
    try:
        as_of = dt.datetime.fromisoformat(snap["as_of"].replace("Z", "+00:00"))
        days = (dt.datetime.now(dt.timezone.utc) - as_of).total_seconds() / 86400
        if days > 21:
            print(f"WARNING  stats snapshot is {days:.0f} days old (>21). "
                  f"Not a failure — run tools\\fetch_stats.py to refresh.")
    except (KeyError, ValueError):
        print("WARNING  stats snapshot has no readable as_of timestamp.")
    return snap


def asset_sources() -> list[tuple[pathlib.Path, pathlib.Path]]:
    return [
        (STATIC / "css", OUT / "css"),
        (STATIC / "js", OUT / "js"),
        (ASSETS / "fonts", OUT / "assets" / "fonts"),
        (ASSETS / "resume", OUT / "assets" / "resume"),
        (ASSETS / "img", OUT / "assets" / "img"),
    ]


def gate_assets(pairs: list[tuple[pathlib.Path, pathlib.Path]]) -> list[tuple[str, str]]:
    """Defect F-02: a missing asset tree raised a bare FileNotFoundError — a
    failure mode with no reason code, which contract 3.6 forbids."""
    out = []
    for src, _dest in pairs:
        if not src.is_dir():
            hint = "  (run: python tools\\subset_fonts.py)" if src.name == "fonts" else ""
            out.append(("ASSET_MISSING", f"{src} not found{hint}"))
    return out


def copy_static() -> None:
    for src, dest in asset_sources():
        shutil.copytree(src, dest)
    shutil.copy2(STATIC / "site.webmanifest", OUT / "site.webmanifest")


def write_sitemap_and_robots() -> None:
    """C-25. Both generated from PAGES, so a new page cannot be forgotten."""
    urls = "\n".join(
        f"  <url><loc>{BASE_URL}{p[4]}</loc></url>" for p in PAGES)
    (OUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{urls}\n</urlset>\n", encoding="utf-8", newline="\n")
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {BASE_URL}/sitemap.xml\n",
        encoding="utf-8", newline="\n")


def get_template_or_refuse(env: Environment, name: str):
    try:
        return env.get_template(name)
    except TemplateNotFound as e:
        raise BuildRefused("TEMPLATE_MISSING", f"{e}") from e


# ---------------------------------------------------------------- build ----

def build() -> int:
    data = load_data()

    tokens_css = (STATIC / "css" / "tokens.css").read_text(encoding="utf-8")
    site_css = (STATIC / "css" / "site.css").read_text(encoding="utf-8")
    defined = {m.group(1) for m in VAR_DEF.finditer(tokens_css)}

    problems: list[tuple[str, str]] = []
    problems += gate_assets(asset_sources())
    problems += gate_color_literal(site_css, "static/css/site.css")
    problems += gate_unknown_token(site_css, defined, "static/css/site.css")

    macros_src = (TPL / "_macros.html.j2").read_text(encoding="utf-8")
    others = {p.name: p.read_text(encoding="utf-8")
              for p in sorted(TPL.glob("*.j2")) if p.name != "_macros.html.j2"}
    problems += gate_mark_source(macros_src, others)
    # Defect F-03: _macros was exempt from the colour-literal gate, so a hex in
    # the one file that defines the motif would have passed. Gate every template.
    for name, src in list(others.items()) + [("_macros.html.j2", macros_src)]:
        problems += gate_color_literal(src, f"templates/{name}")

    if problems:
        return refuse(problems)

    env = Environment(
        loader=FileSystemLoader(str(TPL)),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )

    projects = data["projects"]["projects"]
    snapshot = load_snapshot()
    audit_spec = json.loads((DATA / "audit-spec.json").read_text(encoding="utf-8"))

    measured_path = DATA / "generated" / "audit.json"
    measured_doc = (json.loads(measured_path.read_text(encoding="utf-8"))
                    if measured_path.exists() else {})
    measured = measured_doc.get("measured", {})
    measured_as_of = measured_doc.get("as_of_display", "")

    problems += gate_anchors(projects, snapshot)
    if problems:
        return refuse(problems)

    # Attach each project's anchor so templates never do lookup logic, and a
    # project can never render a figure without its source travelling with it.
    for p in projects:
        repo_url = (p.get("links") or {}).get("repo", "")
        name = repo_url.rstrip("/").rsplit("/", 1)[-1]
        p["_anchor"] = snapshot["repos"][name]

    ctx_common = {
        "profile": data["profile"],
        "projects": projects,
        "flagship": [p for p in projects if p.get("flagship")],
        "roles": data["experience"]["roles"],
        "education": data["experience"]["education"],
        "certifications": data["certifications"]["certifications"],
        "status_note": data["certifications"].get("status_note", ""),
        # R-05, director's ruling: the identity strip renders profile.json's
        # owner-authored `headline_employers` verbatim — curation is authorship,
        # not a code-side omission. The Experience page derives all five roles
        # uncurated from experience.json; that derivation lives in `roles`.
        "employers": data["profile"]["headline_employers"],
        "github": snapshot,
        # Read from tokens.css rather than repeated: contract 3.2 means even the
        # browser-chrome colour has exactly one definition.
        "theme_color": read_token(tokens_css, "--bg"),
        # Markup(), so the source quotes render literally as 'self' rather than
        # &#39;self&#39;. Entity decoding would very probably resolve it at parse
        # time — but meta CSP has no report-only mode, so a policy the parser
        # mishandles blocks every asset on the live site. Not a place to depend
        # on "very probably". The value is built entirely from the CSP dict
        # above, never from data, so marking it safe introduces no injection path.
        "csp": Markup(csp_value()),
        "audit_spec": audit_spec,
        "limitations": audit_spec["a4_limitations"],
        "resolved": audit_spec.get("a4_resolved", []),
        # CI writes measured values into data/generated/audit.json. Absent on
        # any first deploy, and absent now — so the audit page renders
        # "— AT DEPLOY" honestly rather than an optimistic placeholder. That
        # absence is this pipeline's negative control (C-30, C-35).
        "measured": measured,
        "measured_as_of": measured_as_of,
        "nav": NAV,
        "colophon": COLOPHON,
        "visits": VISITS,
    }

    # Defect F-01: pages were written to disk BEFORE the output gates were
    # checked, so a refused build still left bad HTML in _site/ for anyone to
    # serve. Render everything into memory, gate it, and only then write.
    # C-26 structured data, built from the same JSON the pages render from, so
    # markup and content cannot disagree. No email, no phone: C-33 names
    # structured data explicitly, and check_c33.py scans the rendered output.
    profile = data["profile"]
    person_ld = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": profile["name"],
        "url": BASE_URL + "/",
        "jobTitle": profile["headline"].split("|")[0].strip(),
        "description": profile["summary"],
        "address": {"@type": "PostalAddress", "addressLocality": "Hyderabad",
                    "addressCountry": "IN"},
        "sameAs": [profile["links"]["linkedin"], profile["links"]["github"]],
    }
    projects_ld = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": [
            {"@type": "ListItem", "position": i,
             "item": {"@type": "SoftwareSourceCode",
                      "name": p["name"],
                      "description": p["method"],
                      "codeRepository": p["links"]["repo"],
                      "programmingLanguage": "Python",
                      "author": {"@type": "Person", "name": profile["name"]},
                      "version": p["_anchor"]["anchor"]}}
            for i, p in enumerate(projects, 1)],
    }
    ctx_common["person_jsonld"] = Markup(json.dumps(person_ld, indent=2))
    ctx_common["projects_jsonld"] = Markup(json.dumps(projects_ld, indent=2))

    facts = {
        "headline": data["profile"]["headline"],
        "n_projects": len(projects),
        "n_roles": len(data["experience"]["roles"]),
        "years": data["profile"]["years_experience"],
    }

    rendered: list[tuple[str, str]] = []
    for tpl_name, out_rel, nav_id, title, url_path, desc in PAGES:
        tpl = get_template_or_refuse(env, tpl_name)
        html = tpl.render(
            current=nav_id,
            page_title=title,
            page_description=desc.format(**facts),
            canonical=BASE_URL + url_path,
            base_url=BASE_URL,
            **ctx_common)
        problems += gate_inline(html, out_rel)
        problems += gate_mark_drift(html, out_rel)
        problems += gate_mark_drift_paths(html, out_rel)
        rendered.append((out_rel, html))

    if problems:
        return refuse(problems)

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    copy_static()

    write_sitemap_and_robots()

    written = []
    for out_rel, html in rendered:
        dest = OUT / out_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8", newline="\n")
        written.append((out_rel, len(html.encode("utf-8"))))

    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print("Built:")
    for rel, size in written:
        print(f"  {rel:<32} {size:>7,} B")
    print(f"\n  _site total (incl. fonts + PDF): {total:,} B")
    print(f"  content hash: {tree_hash()}")
    return 0


def refuse(problems: list[tuple[str, str]]) -> int:
    print("BUILD REFUSED")
    for reason, detail in problems:
        print(f"  REASON={reason}  {detail}")
    return 1


def tree_hash() -> str:
    """Stable hash of EVERY file in _site — contract 3.7 determinism.

    Defect F-04: this hashed only *.html, so the phrase "the build is
    deterministic" was wider than the evidence — CSS, fonts and the PDF were
    never covered by it. It now covers the whole tree.

    Truncated to 16 hex chars so two runs can be compared by eye. That makes it
    a change-detector for the director, not a security control, and it must
    never be described as one.
    """
    h = hashlib.sha256()
    for f in sorted(OUT.rglob("*")):
        if f.is_file():
            h.update(f.relative_to(OUT).as_posix().encode())
            h.update(f.read_bytes())
    return h.hexdigest()[:16]


# -------------------------------------------------------------- selftest ---

def selftest() -> int:
    """Prove every gate can fail, and that none of them fires on real input."""
    print("SELFTEST — negative controls (each MUST produce its reason code)")
    checks = [
        ("COLOR_LITERAL", lambda: gate_color_literal("a { color: #ff0000; }", "poison")),
        ("COLOR_LITERAL", lambda: gate_color_literal("a { color: rgba(1,2,3,.4); }", "poison")),
        ("TOKEN_UNKNOWN", lambda: gate_unknown_token("a{color:var(--nope)}", {"--bg"}, "poison")),
        ("INLINE_STYLE",  lambda: gate_inline('<p style="color:red">x</p>', "poison")),
        ("INLINE_SCRIPT", lambda: gate_inline("<script>alert(1)</script>", "poison")),
        ("INLINE_SCRIPT", lambda: gate_inline(
            '<script type="text/javascript">alert(1)</script>', "poison")),
        ("MARK_DRIFT",    lambda: gate_mark_drift(
            '<svg class="mark" viewBox="0 0 12 12"></svg><svg class="mark" viewBox="0 0 16 16"></svg>', "poison")),
        ("MARK_DRIFT",    lambda: gate_mark_drift_paths(
            '<svg class="mark"><path stroke-width="1.7"/></svg>'
            '<svg class="mark"><path stroke-width="2.4"/></svg>', "poison")),
        ("MARK_SOURCE",   lambda: gate_mark_source(
            '<svg class="mark"></svg>', {"rogue.j2": '<svg class="mark--check mark"></svg>'})),
        ("ASSET_MISSING", lambda: gate_assets([(ROOT / "no-such-dir", OUT / "x")])),
    ]
    ok = True
    for expected, fn in checks:
        found = [r for r, _d in fn()]
        if expected in found:
            print(f"  [PASS] {expected:<16} refused as expected")
        else:
            print(f"  [FAIL] {expected:<16} NOT refused (got {found})")
            ok = False

    # The three reason codes raised as exceptions rather than returned as
    # problems. Defect F-05: these had no negative control at all, so "a
    # distinct reason code per failure mode" (contract 3.6) was asserted for
    # four codes that had never once been seen to fire.
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        for expected, setup in [
            ("DATA_MISSING", lambda: None),
            ("DATA_MALFORMED", lambda: [
                (tmp / f"{n}.json").write_text("{}" if n != "profile" else "{not json",
                                               encoding="utf-8") for n in DATA_FILES]),
        ]:
            setup()
            try:
                load_data(tmp)
                print(f"  [FAIL] {expected:<16} NOT refused")
                ok = False
            except BuildRefused as e:
                if e.reason == expected:
                    print(f"  [PASS] {expected:<16} refused as expected")
                else:
                    print(f"  [FAIL] {expected:<16} got REASON={e.reason}")
                    ok = False

    env = Environment(loader=FileSystemLoader(str(TPL)))
    try:
        get_template_or_refuse(env, "no-such-template.j2")
        print(f"  [FAIL] {'TEMPLATE_MISSING':<16} NOT refused")
        ok = False
    except BuildRefused as e:
        state = "PASS" if e.reason == "TEMPLATE_MISSING" else "FAIL"
        print(f"  [{state}] {'TEMPLATE_MISSING':<16} refused as expected")
        ok = ok and state == "PASS"

    print("\nSELFTEST — positive controls (real input MUST NOT trip any gate)")
    tokens_css = (STATIC / "css" / "tokens.css").read_text(encoding="utf-8")
    site_css = (STATIC / "css" / "site.css").read_text(encoding="utf-8")
    defined = {m.group(1) for m in VAR_DEF.finditer(tokens_css)}
    macros_src = (TPL / "_macros.html.j2").read_text(encoding="utf-8")
    others = {p.name: p.read_text(encoding="utf-8")
              for p in sorted(TPL.glob("*.j2")) if p.name != "_macros.html.j2"}

    positives = [
        ("site.css colour literals", gate_color_literal(site_css, "site.css")),
        ("tokens.css token refs", gate_unknown_token(tokens_css, defined, "tokens.css")),
        ("site.css token refs", gate_unknown_token(site_css, defined, "site.css")),
        ("_macros colour literals", gate_color_literal(macros_src, "_macros.html.j2")),
        ("mark single source", gate_mark_source(macros_src, others)),
        ("real asset trees present", gate_assets(asset_sources())),
        ("ld+json data block accepted (HTML spec step 13, not step 21)",
         gate_inline('<script type="application/ld+json">{"a":1}</script>', "ld")),
    ]
    for label, found in positives:
        if found:
            print(f"  [FAIL] {label}: unexpectedly refused -> {found}")
            ok = False
        else:
            print(f"  [PASS] {label}: clean, no false refusal")

    try:
        data = load_data()
        print(f"  [PASS] real data loads: {', '.join(sorted(data))}")
    except BuildRefused as e:
        print(f"  [FAIL] real data refused: {e}")
        ok = False

    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    try:
        return selftest() if args.selftest else build()
    except BuildRefused as e:
        print("BUILD REFUSED")
        print(f"  {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
