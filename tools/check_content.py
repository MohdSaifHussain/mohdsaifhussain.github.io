"""Content rules that a script can enforce.  P3.2 / D9.

Three checks, each with both controls:

EM_DASH (defect D-08) — C-27 bans em-dashes in RESUME-DERIVED text. That ban
cannot be site-wide: the frozen h1 and the charter's own colophon both contain
em-dashes, so a global rule would be unimplementable against the design
authority. Scope is therefore exactly three places, and the scope is the point:
  - data/experience.json
  - the rendered Experience page
  - the web-resume PDF
Chrome written into the Experience template is bound by the same rule, because
the check runs on the rendered output rather than only on the data.

COUNT_LITERAL (defect D-07) — every count comes from len(data). A literal
two-digit number in front of ENTRIES / ROLES / PROJECTS etc. in a template
means someone typed a number a script should have written (C-34). Section
numbering ("01 / 04 — IDENTITY") is structural, not a data count, and is
deliberately NOT flagged.

INLINE_MARKUP (C-18) — no style attribute, no inline script body, checked on
the rendered output as well as at build time.

Usage (PowerShell):
    python tools\\check_content.py
    python tools\\check_content.py --selftest
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")     # defect D-13
sys.stderr.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
PDF = ROOT / "assets" / "resume" / "MohdSaifHussain_Resume_Web.pdf"

EM_DASH = "—"

# Nouns whose counts must always be computed. A literal in front of one of
# these is a number somebody typed.
COUNTED = r"(?:ENTRIES|ROLES|PROJECTS|CERTIFICATIONS|COURSES|YEARS|TESTS)"
COUNT_LITERAL = re.compile(rf"(?<![\w/])\d{{1,3}}\s+{COUNTED}\b")

JINJA = re.compile(r"\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\}", re.S)

INLINE_STYLE_ATTR = re.compile(r"<[^>]+\sstyle\s*=", re.I)
# See build.py for the citation: an application/ld+json block returns at step 13
# of HTML's "prepare the script element" and never reaches the step-21 CSP
# check, so it is data, not executable script.
INLINE_SCRIPT = re.compile(
    r"<script(?![^>]*\bsrc=)(?![^>]*\btype=[\"']application/ld\+json[\"'])[^>]*>\s*\S", re.I)


MAIN = re.compile(r"<main\b[^>]*>(.*?)</main>", re.S | re.I)


def main_of(html: str) -> str:
    """The page's own content, excluding nav/footer chrome shared by all pages."""
    m = MAIN.search(html)
    return m.group(1) if m else html


def check_em_dash(text: str, where: str) -> list[tuple[str, str]]:
    out = []
    for m in re.finditer(re.escape(EM_DASH), text):
        line = text[:m.start()].count("\n") + 1
        context = text[max(0, m.start() - 40):m.start() + 40].replace("\n", " ")
        out.append(("EM_DASH", f"{where}:{line}  …{context.strip()}…"))
    return out


def check_count_literal(template_src: str, where: str) -> list[tuple[str, str]]:
    """Run on template SOURCE with Jinja expressions stripped: what remains is
    literal text the author typed."""
    literal_only = JINJA.sub(" ", template_src)
    return [("COUNT_LITERAL", f"{where}  '{m.group()}' — must come from len(data)")
            for m in COUNT_LITERAL.finditer(literal_only)]


def check_inline(html: str, where: str) -> list[tuple[str, str]]:
    out = []
    if INLINE_STYLE_ATTR.search(html):
        out.append(("INLINE_MARKUP", f"{where}: style= attribute in output"))
    if INLINE_SCRIPT.search(html):
        out.append(("INLINE_MARKUP", f"{where}: inline <script> body in output"))
    return out


def pdf_text() -> str:
    from pdfminer.high_level import extract_text
    return extract_text(str(PDF))


def run() -> int:
    problems: list[tuple[str, str]] = []

    # --- EM_DASH, in its three scoped places only ---
    xp_json = ROOT / "data" / "experience.json"
    problems += check_em_dash(xp_json.read_text(encoding="utf-8"), "data/experience.json")

    xp_page = SITE / "experience" / "index.html"
    if not xp_page.exists():
        print("REASON=SITE_MISSING  run python build.py first")
        return 1

    # Defect D-22: scoping this to the whole rendered page caught site chrome
    # shared by all five pages — the <title> separator, and the footer's
    # "VISITS —", which is the DESIGNED state per handoff §3. Enforcing the
    # rule there would have forced a change that violates the design authority.
    # C-27's em-dash rule is about resume-derived TEXT, and that lives in
    # <main>. Chrome inside <main> is still bound, which is the point.
    problems += check_em_dash(main_of(xp_page.read_text(encoding="utf-8")),
                              "_site/experience/index.html <main>")
    problems += check_em_dash(pdf_text(), "web-resume PDF")

    # --- COUNT_LITERAL, across every template ---
    for tpl in sorted((ROOT / "templates").glob("*.j2")):
        problems += check_count_literal(tpl.read_text(encoding="utf-8"), f"templates/{tpl.name}")

    # --- INLINE_MARKUP, across every rendered page ---
    for page in sorted(SITE.rglob("*.html")):
        problems += check_inline(page.read_text(encoding="utf-8"),
                                 str(page.relative_to(SITE)))

    if problems:
        print("CONTENT CHECK FAILED")
        for reason, detail in problems:
            print(f"  REASON={reason}  {detail}")
        return 1
    print("CONTENT OK — em-dash scope clean, no typed counts, no inline markup")
    return 0


def selftest() -> int:
    ok = True
    print("SELFTEST — both controls for each rule\n")
    cases = [
        ("em dash in resume-derived text MUST trip",
         lambda: check_em_dash(f"Managed ops {EM_DASH} led the team", "fixture"),
         "EM_DASH", True),
        ("hyphens and middle dots MUST NOT trip",
         lambda: check_em_dash("Jan 2026 - Apr 2026 · Hyderabad", "fixture"),
         "EM_DASH", False),
        ("typed count MUST trip",
         lambda: check_count_literal("<span>05 ENTRIES</span>", "fixture"),
         "COUNT_LITERAL", True),
        ("computed count MUST NOT trip",
         lambda: check_count_literal("<span>{{ '%02d' % (projects|length) }} ENTRIES</span>",
                                     "fixture"),
         "COUNT_LITERAL", False),
        ("section numbering MUST NOT trip (structural, not a data count)",
         lambda: check_count_literal("<span>01 / 04 — IDENTITY</span>", "fixture"),
         "COUNT_LITERAL", False),
        ("style attribute MUST trip",
         lambda: check_inline('<p style="color:red">x</p>', "fixture"),
         "INLINE_MARKUP", True),
        ("external script MUST NOT trip",
         lambda: check_inline('<script src="/js/clock.js"></script>', "fixture"),
         "INLINE_MARKUP", False),

        # Defect D-22 locked in as controls: page content is bound by the
        # em-dash rule, shared chrome outside <main> is not.
        ("em dash inside <main> MUST trip",
         lambda: check_em_dash(
             main_of(f"<title>x — y</title><main><p>Ops {EM_DASH} led</p></main>"), "fixture"),
         "EM_DASH", True),
        ("handoff-mandated 'VISITS —' in the footer MUST NOT trip",
         lambda: check_em_dash(
             main_of('<main><p>clean</p></main><footer>VISITS —</footer>'), "fixture"),
         "EM_DASH", False),
        ("the <title> separator MUST NOT trip",
         lambda: check_em_dash(
             main_of("<title>Experience — MOHD SAIF HUSSAIN</title><main><p>ok</p></main>"),
             "fixture"),
         "EM_DASH", False),
    ]
    for label, fn, reason, must_trip in cases:
        found = reason in [r for r, _ in fn()]
        good = found == must_trip
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] "
              f"{'refused' if found else 'accepted':<8} {label}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    return selftest() if args.selftest else run()


if __name__ == "__main__":
    raise SystemExit(main())
