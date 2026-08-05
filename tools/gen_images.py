"""Generate the OG image and favicon set from the design tokens.  P3.2 / D10.

C-25 requires a real Open Graph image and a favicon set + web manifest.
Defect D-09: none existed, and the committed direction is pure typography, so
there was nothing to photograph. Everything here is DRAWN from tokens.css
values and the same check-mark geometry the site uses, so the icons cannot
drift from the site's own design.

MAINTENANCE TOOL, NOT A CI STEP — the same lesson as D-18/D-23/D-24. This needs
the upstream TTFs in build/fonts-src/, which is gitignored. Its OUTPUT is
committed and served. CI never runs this, so CI can never fail on a font file
that only exists on one machine.

Usage (PowerShell):
    python tools\\gen_images.py
"""

from __future__ import annotations

import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

from PIL import Image, ImageDraw, ImageFont     # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS = ROOT / "static" / "css" / "tokens.css"
SRC = ROOT / "build" / "fonts-src"
OUT_IMG = ROOT / "assets" / "img"
SERIF = SRC / "InstrumentSerif-Regular.ttf"
MONO = SRC / "IBMPlexMono-Medium.ttf"

# The check-mark path from templates/_macros.html.j2, in its 12x12 viewBox.
# Kept in the same proportions so the favicon IS the site's mark.
CHECK_PATH = [(1.6, 6.3), (4.5, 9.2), (10.4, 3.3)]
CHECK_STROKE = 1.7
VIEWBOX = 12.0


def token(name: str) -> str:
    """Read a colour straight from tokens.css — never a second copy of a hex."""
    m = re.search(rf"^\s*{re.escape(name)}:\s*(#[0-9a-fA-F]{{3,8}})\s*;",
                  TOKENS.read_text(encoding="utf-8"), re.M)
    if not m:
        sys.exit(f"REASON=TOKEN_UNKNOWN  {name} not found in tokens.css")
    return m.group(1)


def require_sources() -> None:
    missing = [p for p in (SERIF, MONO) if not p.exists()]
    if missing:
        sys.exit("REASON=SRC_MISSING  " + ", ".join(str(p) for p in missing)
                 + "  (run: python tools\\subset_fonts.py)")


def draw_check(size: int, bg: str, accent: str, pad: float = 0.22) -> Image.Image:
    """The motif, drawn at any size from the one geometry."""
    img = Image.new("RGBA", (size, size), bg)
    d = ImageDraw.Draw(img)
    inner = size * (1 - 2 * pad)
    scale = inner / VIEWBOX
    off = size * pad
    pts = [(off + x * scale, off + y * scale) for x, y in CHECK_PATH]
    d.line(pts, fill=accent, width=max(2, round(CHECK_STROKE * scale)), joint="curve")
    return img


def make_favicons(bg: str, accent: str) -> list[str]:
    written = []
    OUT_IMG.mkdir(parents=True, exist_ok=True)
    for size, name in [(180, "apple-touch-icon.png"), (192, "icon-192.png"),
                       (512, "icon-512.png")]:
        p = OUT_IMG / name
        draw_check(size, bg, accent).convert("RGB").save(p)
        written.append(f"{name} ({size}x{size})")

    ico = ROOT / "assets" / "img" / "favicon.ico"
    base = draw_check(64, bg, accent).convert("RGB")
    base.save(ico, sizes=[(16, 16), (32, 32), (48, 48), (64, 64)])
    written.append("favicon.ico (16/32/48/64)")
    return written


def make_og(bg: str, ink: str, accent: str, dim: str, wordmark: str, line: str) -> str:
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    gutter = 72

    f_word = ImageFont.truetype(str(SERIF), 34)
    f_line = ImageFont.truetype(str(SERIF), 62)
    f_meta = ImageFont.truetype(str(MONO), 20)

    # Wordmark, letterspaced by hand — PIL has no letter-spacing.
    x = gutter
    for ch in wordmark:
        d.text((x, gutter), ch, font=f_word, fill=ink)
        x += d.textlength(ch, font=f_word) + 7

    d.line([(gutter, gutter + 66), (W - gutter, gutter + 66)], fill=ink, width=2)

    # Identity line, wrapped to the gutter width.
    words, lines, cur = line.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f_line) > W - 2 * gutter:
            lines.append(cur)
            cur = w
        else:
            cur = trial
    lines.append(cur)

    y = gutter + 120
    for ln in lines[:5]:
        d.text((gutter, y), ln, font=f_line, fill=ink)
        y += 74

    d.line([(gutter, H - 108), (W - gutter, H - 108)], fill=accent, width=2)
    d.text((gutter, H - 82), "GOVERNED, AUDITED, TRACEABLE", font=f_meta, fill=dim)

    # The motif, bottom-right.
    mark = draw_check(56, bg, accent, pad=0.1)
    img.paste(mark.convert("RGB"), (W - gutter - 56, H - 96))

    p = OUT_IMG / "og.png"
    img.save(p, optimize=True)
    return f"og.png (1200x630, {p.stat().st_size:,} B)"


def make_manifest(bg: str, accent: str, name: str) -> str:
    import json
    manifest = {
        "name": name,
        "short_name": name.split()[0],
        "start_url": "/",
        "display": "browser",
        "background_color": bg,
        "theme_color": accent,
        "icons": [
            {"src": "/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }
    p = ROOT / "static" / "site.webmanifest"
    p.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8", newline="\n")
    return "site.webmanifest"


def main() -> int:
    import json
    require_sources()
    bg, ink, accent, dim = (token("--bg"), token("--ink"),
                            token("--accent"), token("--dim"))
    profile = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))

    print(f"tokens: bg={bg} ink={ink} accent={accent}")
    for line in make_favicons(bg, accent):
        print(f"  {line}")
    print(f"  {make_og(bg, ink, accent, dim, profile['wordmark'], profile['identity_line'])}")
    print(f"  {make_manifest(bg, accent, profile['name'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
