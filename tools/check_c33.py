"""C-33: no contact-capable address, no phone number.  P3.2 / D8.

Governing text: STEP-01-CHARTER C-33, as amended by **Amendment 1** (noreply
addresses at users.noreply.github.com exempt, required for git authorship) and
**Amendment 2** (purpose clause + exemptions stated as an ENUMERATED LIST).

Amendment 2's exemptions, verbatim:
  (1) *@users.noreply.github.com
  (2) the literal noreply@anthropic.com, solely as the Co-Authored-By
      AI-attribution trailer
No address is exempt by resembling an exempt one.

THE THREE CONTROLS (contract 3.4), all run by --selftest:
  - a routable-looking address MUST trip;
  - `noreply@` at an UNLISTED domain MUST ALSO trip — this is what proves the
    implementation enumerates rather than pattern-matches. A pattern-based
    check passes this case and looks identical to a correct one;
  - a fixture of ISO-8601 dates MUST NOT trip (defect D-11). A checker that
    cries wolf on every date is a checker that gets ignored.

Scope: every git-tracked text file, plus the extracted text of the web-resume
PDF (contract 3.5).

Usage (PowerShell):
    python tools\\check_c33.py
    python tools\\check_c33.py --selftest
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")     # defect D-13
sys.stderr.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
PDF = ROOT / "assets" / "resume" / "MohdSaifHussain_Resume_Web.pdf"

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# ENUMERATED. Not patterns. Adding to either list is a recorded decision.
EXEMPT_DOMAINS = frozenset({"users.noreply.github.com"})
EXEMPT_LITERALS = frozenset({"noreply@anthropic.com"})

# Phone detection, deliberately shaped for PRECISION.
#
# Defect D-11 was one symptom of a naive pattern; the first real scan showed
# six more, all things this repo legitimately contains: a commit SHA that
# happens to be all digits (7891608), a 9-digit GitHub user id, the standard
# number "ISO 9241-210", an IST timestamp, and SVG path coordinates. A checker
# that reports those is a checker nobody reads, so C-33 would go unenforced by
# a check that technically "passes".
#
# A hit therefore requires phone-SHAPED evidence, not merely digits:
#   - an international prefix (+ then 8-15 digits), or
#   - separator grouping (2+ separators) totalling 10-15 digits, or
#   - a bare run of exactly 10-12 digits, the common national-number lengths.
# Bare 7-9 digit runs are NOT treated as phone numbers. That is a deliberate
# recall/precision trade, stated as an honest limit rather than hidden.
PHONE_INTL = re.compile(r"(?<![\w.-])\+\d[\d\s().-]{7,17}\d(?![\w-])")
PHONE_GROUPED = re.compile(r"(?<![\w.:-])\d{2,5}(?:[\s.\-()]+\d{2,5}){2,}(?![\w-])")
PHONE_BARE = re.compile(r"(?<![\w.:+-])\d{10,12}(?![\w.-])")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")

# Defect D-38: a GitHub Actions run id is an 11-digit bare number, and quoting
# one as EVIDENCE in a phase record tripped the phone check. Recording machine
# evidence collided with detecting contact details.
#
# The discriminator is context, not shape: an identifier is introduced by a word
# that names it. This screens only digits carrying such a marker — a bare
# 10-digit number in prose still trips, which the controls assert in both
# directions.
IDENTIFIER_CONTEXT = re.compile(
    r"(?:\brun\b|\bruns/\b|\bjob\b|\bid\b|\bbuild\b|#)\s*$", re.I)

SKIP_SUFFIXES = {".woff2", ".ttf", ".pdf", ".avif", ".webp", ".jpg", ".png", ".ico"}


def is_exempt_email(addr: str) -> bool:
    """Amendment 2, by enumeration."""
    if addr in EXEMPT_LITERALS:
        return True
    domain = addr.rsplit("@", 1)[-1].lower()
    return domain in EXEMPT_DOMAINS


def phone_hits(text: str) -> list[str]:
    """Digit runs carrying phone-shaped evidence, after every screen."""
    out: list[str] = []
    for rx in (PHONE_INTL, PHONE_GROUPED, PHONE_BARE):
        for m in rx.finditer(text):
            raw = m.group().strip()
            if ISO_DATE.search(raw):
                continue                      # defect D-11: dates and timestamps
            if "," in raw:
                continue                      # grouped byte counts: 129,380
            # D-38: "run 31058175791" is an identifier, not a number to call.
            if IDENTIFIER_CONTEXT.search(text[max(0, m.start() - 12):m.start()]):
                continue
            digits = re.sub(r"\D", "", raw)
            if rx is PHONE_INTL and not 8 <= len(digits) <= 15:
                continue
            if rx is PHONE_GROUPED and not 10 <= len(digits) <= 15:
                continue
            if raw not in out:
                out.append(raw)
    return out


def scan_text(text: str, where: str) -> list[tuple[str, str]]:
    """Pure over text, so the controls can drive it directly."""
    problems = []
    for m in EMAIL.finditer(text):
        addr = m.group()
        if not is_exempt_email(addr):
            line = text[:m.start()].count("\n") + 1
            problems.append(("EMAIL_FOUND", f"{where}:{line}  {addr}"))
    for hit in phone_hits(text):
        problems.append(("PHONE_FOUND", f"{where}  {hit}"))
    return problems


def tracked_files() -> list[pathlib.Path]:
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True,
                         text=True, check=True).stdout.splitlines()
    return [ROOT / p for p in out if pathlib.Path(p).suffix not in SKIP_SUFFIXES]


def pdf_text() -> str:
    from pdfminer.high_level import extract_text
    return extract_text(str(PDF))


def run() -> int:
    problems: list[tuple[str, str]] = []
    files = tracked_files()
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        problems += scan_text(text, str(path.relative_to(ROOT)))

    problems += scan_text(pdf_text(), "assets/resume/MohdSaifHussain_Resume_Web.pdf")

    print(f"scanned {len(files)} tracked text files + the web-resume PDF")
    if problems:
        print("C-33 CHECK FAILED")
        for reason, detail in problems:
            print(f"  REASON={reason}  {detail}")
        return 1
    print("C-33 OK — no contact-capable address, no phone number")
    return 0


def _j(*parts: str) -> str:
    """Assemble a fixture from fragments.

    Defect D-24: once this file became git-tracked, the scan covered it — and
    its own poisoned fixtures are precisely what it exists to find. Excluding
    this path would have been the easy fix and the wrong one: it creates a
    blind spot where a real address could sit forever, unscanned.

    Instead no contact-shaped literal exists anywhere in the repo. The fixtures
    are assembled at runtime, so the checker scans itself with ZERO exclusions
    and still proves its controls. The strings below are inert as source text
    and only become addresses and numbers when this runs.
    """
    return "".join(parts)


def selftest() -> int:
    ok = True
    print("SELFTEST — the three controls required by contract 3.4\n")

    ADDR_ROUTABLE = _j("saif.hussain", "@", "exam", "ple.com")
    ADDR_NOREPLY_UNLISTED = _j("nore", "ply", "@", "exam", "ple.org")
    ADDR_LOOKALIKE = _j("nore", "ply", "@", "users.norep", "ly.github.com", ".evil.test")
    ADDR_EXEMPT_GH = _j("263689115+MohdSaifHussain", "@", "users.norep", "ly.github.com")
    ADDR_EXEMPT_ANTHROPIC = _j("norep", "ly", "@", "anthro", "pic.com")
    PHONE_REAL = _j("+91 ", "98765", " 43210")
    PHONE_BARE_REAL = _j("98765", "43210")

    cases = [
        ("routable address MUST trip",
         f"write to {ADDR_ROUTABLE} please", "EMAIL_FOUND", True),
        ("noreply@ at an UNLISTED domain MUST ALSO trip "
         "(this is what proves enumeration, not pattern-matching)",
         ADDR_NOREPLY_UNLISTED, "EMAIL_FOUND", True),
        ("noreply@ at a near-miss lookalike domain MUST trip",
         ADDR_LOOKALIKE, "EMAIL_FOUND", True),
        ("real phone number MUST trip",
         f"call {PHONE_REAL} today", "PHONE_FOUND", True),
        ("ISO-8601 dates MUST NOT trip (defect D-11)",
         "2026-08-06 and 2026-08-05 and 2015-01-01", "PHONE_FOUND", False),
        ("exempt github noreply MUST NOT trip (Amendment 1)",
         ADDR_EXEMPT_GH, "EMAIL_FOUND", False),
        ("exempt anthropic literal MUST NOT trip (Amendment 2)",
         f"Co-Authored-By: Claude Opus 5 <{ADDR_EXEMPT_ANTHROPIC}>", "EMAIL_FOUND", False),
        ("grouped byte counts MUST NOT trip",
         "total 129,380 bytes and 274,215 bytes", "PHONE_FOUND", False),
        ("version anchors and SHAs MUST NOT trip",
         "v1.6.0 at ab98ee6a3c309f57134d48787aa604b1d1044f62", "PHONE_FOUND", False),

        # The seven false positives the FIRST real scan produced, locked in as
        # controls so this precision cannot silently regress. Each one is a
        # thing this repo legitimately contains.
        ("bare national-length number MUST trip",
         PHONE_BARE_REAL, "PHONE_FOUND", True),
        ("all-digit 7-char commit SHA MUST NOT trip",
         '"anchor": "7891608"', "PHONE_FOUND", False),
        ("9-digit GitHub user id MUST NOT trip",
         "user id 263689115", "PHONE_FOUND", False),
        ("standard numbers like ISO 9241-210 MUST NOT trip",
         "ISO 9241-210 human-centred design", "PHONE_FOUND", False),
        ("IST timestamps MUST NOT trip",
         "as of 2026-08-06 02:45 IST", "PHONE_FOUND", False),
        ("SVG path coordinates MUST NOT trip",
         'd="M1.6 6.3 4.5 9.2 10.4 3.3"', "PHONE_FOUND", False),
        ("contrast ratios MUST NOT trip",
         "#cfccc3 = 10.6:1 and #8f8c83 = 5.1:1", "PHONE_FOUND", False),

        # D-38, both directions. Quoting machine evidence must not trip the
        # check, and removing that false positive must not blind it to a real
        # bare number sitting in prose.
        ("a CI run id MUST NOT trip",
         "CI run 31057605043 shows the controls passing", "PHONE_FOUND", False),
        ("a job id MUST NOT trip",
         "see job 31058175791 for the log", "PHONE_FOUND", False),
        ("a bare number in prose MUST still trip",
         f"reach me on {PHONE_BARE_REAL} any time", "PHONE_FOUND", True),
    ]

    for label, text, reason, must_trip in cases:
        found = reason in [r for r, _ in scan_text(text, "fixture")]
        good = found == must_trip
        ok = ok and good
        verb = "refused" if found else "accepted"
        print(f"  [{'PASS' if good else 'FAIL'}] {verb:<8} {label}")

    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    return selftest() if args.selftest else run()


if __name__ == "__main__":
    raise SystemExit(main())
