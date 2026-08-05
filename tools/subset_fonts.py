"""Download, verify and subset the two self-hosted faces.  P3.1 / D4.

Charter C-04 (self-hosted, no third-party), C-03 (transfer budget), charter §5
(two typefaces maximum).  Handoff §6 (self-host woff2, subset).

Official sources, fetched not remembered (doctrine rule 3):
  Instrument Serif  https://github.com/google/fonts/tree/main/ofl/instrumentserif
  IBM Plex Mono     https://github.com/google/fonts/tree/main/ofl/ibmplexmono
Both SIL Open Font License 1.1.  IBM Plex Mono's upstream origin is
https://github.com/IBM/plex (@ibm/plex-mono@2.5.0); google/fonts is used for
both faces because it publishes static instances at exactly the weights the
handoff specifies, under one consistent licence tree.

THE COVERAGE GATE (contract requirement 3.5)
A missing glyph does not raise an error at runtime.  It silently falls back to
a system font, which means a third typeface, rendering differently on every
operating system, with every test still green.  So absence is a build failure
here, not a warning.  Run with --report to see the matrix without building.

Usage (PowerShell):
    python tools\\subset_fonts.py --report
    python tools\\subset_fonts.py
    python tools\\subset_fonts.py --selftest
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import sys
import unicodedata
import urllib.request

# This build runs on a cp1252 console (defect D-13); every stream that may
# carry a mark, a dash or an arrow is pinned to UTF-8 explicitly.
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from fontTools.subset import Subsetter, Options          # noqa: E402
from fontTools.ttLib import TTFont                        # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "build" / "fonts-src"
OUT = ROOT / "assets" / "fonts"

BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl/"

# stem -> (upstream path, face family, css weight, css style)
FACES = {
    "InstrumentSerif-Regular": ("instrumentserif/InstrumentSerif-Regular.ttf", "serif", 400, "normal"),
    "InstrumentSerif-Italic":  ("instrumentserif/InstrumentSerif-Italic.ttf",  "serif", 400, "italic"),
    "IBMPlexMono-Regular":     ("ibmplexmono/IBMPlexMono-Regular.ttf",         "mono",  400, "normal"),
    "IBMPlexMono-Medium":      ("ibmplexmono/IBMPlexMono-Medium.ttf",          "mono",  500, "normal"),
    "IBMPlexMono-SemiBold":    ("ibmplexmono/IBMPlexMono-SemiBold.ttf",        "mono",  600, "normal"),
}

ASCII = list(range(0x20, 0x7F))

# Derived from the committed design + data by enumeration, NOT from memory.
# tools/scan_glyphs.py reproduces this list from source content.
SERIF_REQUIRED = ASCII + [0x00A7, 0x00B7, 0x00D7, 0x2013, 0x2014]
MONO_REQUIRED = SERIF_REQUIRED + [0x2192, 0x2193, 0x2197, 0x2264, 0x2265, 0x2713]

# Carried in the subset though not strictly required, at negligible cost:
# U+2022 BULLET is the only filled round mark either face carries.
EXTRA = [0x2022]

REQUIRED = {"serif": SERIF_REQUIRED, "mono": MONO_REQUIRED}

# Known absent from ALL five faces — defect D-14, resolved in markup, not here.
KNOWN_ABSENT = {0x25CF: "BLACK CIRCLE", 0x2717: "BALLOT X"}


def name_of(cp: int) -> str:
    try:
        return unicodedata.name(chr(cp))
    except ValueError:
        return "<unnamed>"


def download() -> None:
    SRC.mkdir(parents=True, exist_ok=True)
    for stem, (rel, *_rest) in FACES.items():
        dest = SRC / f"{stem}.ttf"
        if dest.exists():
            continue
        data = urllib.request.urlopen(BASE + rel, timeout=60).read()
        dest.write_bytes(data)
        print(f"  fetched {stem}.ttf  {len(data):,} B  "
              f"sha256={hashlib.sha256(data).hexdigest()[:16]}")


def coverage() -> tuple[dict[str, set[int]], list[tuple[str, int]]]:
    """Return per-face cmaps and the list of (face, codepoint) gaps that matter."""
    cmaps: dict[str, set[int]] = {}
    for stem in FACES:
        path = SRC / f"{stem}.ttf"
        if not path.exists():
            sys.exit(f"REASON=SRC_MISSING  {path} not downloaded")
        font = TTFont(str(path), lazy=True)
        cmaps[stem] = set(font.getBestCmap())
        font.close()

    gaps: list[tuple[str, int]] = []
    for stem, (_rel, family, *_r) in FACES.items():
        for cp in REQUIRED[family]:
            if cp not in cmaps[stem]:
                gaps.append((stem, cp))
    return cmaps, gaps


def shipped_coverage() -> tuple[dict[str, set[int]], list[tuple[str, int]]]:
    """Coverage of the woff2 files that ACTUALLY SHIP, not the upstream TTFs.

    Defect D-18, found by CI: coverage() reads build/fonts-src/*.ttf, which is
    gitignored. Those tests passed locally only because the downloads happened
    to be present, and — worse — they asserted a property of the upstream font
    rather than of the artifact the browser loads. A subsetting bug that
    dropped a glyph would not have failed them.

    This reads assets/fonts/*.woff2, which is committed and is what ships.
    """
    cmaps: dict[str, set[int]] = {}
    for stem in FACES:
        path = OUT / f"{stem}.woff2"
        if not path.exists():
            raise SystemExit(f"REASON=SUBSET_MISSING  {path} not built")
        font = TTFont(str(path), lazy=True)
        cmaps[stem] = set(font.getBestCmap())
        font.close()

    gaps: list[tuple[str, int]] = []
    for stem, (_rel, family, *_r) in FACES.items():
        for cp in REQUIRED[family]:
            if cp not in cmaps[stem]:
                gaps.append((stem, cp))
    return cmaps, gaps


def report(cmaps: dict[str, set[int]]) -> None:
    every = sorted(set(MONO_REQUIRED) | set(KNOWN_ABSENT) | set(EXTRA))
    shown = [cp for cp in every if cp > 0x7E]
    stems = list(FACES)
    short = {s: s.replace("InstrumentSerif-", "IS-").replace("IBMPlexMono-", "PM-") for s in stems}
    print(f"\n{'CP':<8}{'CH':<4}{'NAME':<26}" + "".join(f"{short[s]:<12}" for s in stems))
    print("-" * (38 + 12 * len(stems)))
    for cp in shown:
        row = f"U+{cp:04X}  {chr(cp):<4}{name_of(cp)[:25]:<26}"
        for s in stems:
            row += f"{('yes' if cp in cmaps[s] else 'NO'):<12}"
        print(row)
    print(f"\nASCII U+0020-007E:")
    for s in stems:
        missing = [c for c in ASCII if c not in cmaps[s]]
        print(f"  {s:<28}{'complete' if not missing else f'MISSING {missing}'}")
    print("\nKnown absent from every face (defect D-14, handled in markup):")
    for cp, nm in KNOWN_ABSENT.items():
        print(f"  U+{cp:04X} {chr(cp)}  {nm}")


def subset_all(cmaps: dict[str, set[int]]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for stem, (_rel, family, weight, style) in FACES.items():
        wanted = sorted(set(REQUIRED[family]) | set(EXTRA))
        keep = [cp for cp in wanted if cp in cmaps[stem]]

        font = TTFont(str(SRC / f"{stem}.ttf"))
        opts = Options()
        opts.flavor = "woff2"
        opts.desubroutinize = True
        opts.layout_features = ["kern", "liga", "calt"]
        opts.name_IDs = ["*"]          # keep the OFL name records (licence)
        opts.notdef_outline = True
        sub = Subsetter(options=opts)
        sub.populate(unicodes=keep)
        sub.subset(font)

        dest = OUT / f"{stem}.woff2"
        font.save(str(dest))
        font.close()
        size = dest.stat().st_size
        total += size
        src_size = (SRC / f"{stem}.ttf").stat().st_size
        print(f"  {stem:<28} {src_size:>8,} -> {size:>7,} B  "
              f"({len(keep)} glyphs, -{100 - size * 100 // src_size}%)")
    print(f"\n  TOTAL SHIPPED FONT BYTES: {total:,}  (C-03 budget is 500,000 for the whole first view)")


def selftest(cmaps: dict[str, set[int]]) -> int:
    """Prove the gate can fail, and that it does not fail on everything.

    doctrine rule 5: a check that has only ever passed is a decoration.
    """
    print("SELFTEST")
    ok = True

    # Negative control: a codepoint no face carries MUST be reported as a gap.
    poisoned = dict(REQUIRED)
    poisoned["serif"] = SERIF_REQUIRED + [0x2717]
    found = [cp for cp in poisoned["serif"] if cp not in cmaps["InstrumentSerif-Regular"]]
    if found == [0x2717]:
        print("  [PASS] negative control: injected U+2717 detected as a gap  REASON=GLYPH_MISSING")
    else:
        print(f"  [FAIL] negative control: expected [0x2717], got {found}")
        ok = False

    # Positive control: the real required set must NOT trip the gate, or a gate
    # that refuses everything would look identical to a gate that works.
    _cm, gaps = coverage()
    if not gaps:
        print("  [PASS] positive control: real required set is fully covered, no false gaps")
    else:
        print(f"  [FAIL] positive control: unexpected gaps {[(s, hex(c)) for s, c in gaps]}")
        ok = False
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true", help="print the coverage matrix, build nothing")
    ap.add_argument("--selftest", action="store_true", help="prove the coverage gate can fail")
    args = ap.parse_args()

    print("Fetching official sources...")
    download()
    cmaps, gaps = coverage()

    if args.report:
        report(cmaps)
        return 0
    if args.selftest:
        return selftest(cmaps)

    report(cmaps)
    if gaps:
        print("\nBUILD REFUSED  REASON=GLYPH_MISSING")
        for stem, cp in gaps:
            print(f"  {stem} lacks U+{cp:04X} {chr(cp)} ({name_of(cp)})")
        return 1

    print("\nSubsetting...")
    subset_all(cmaps)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
