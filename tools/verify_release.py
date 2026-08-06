"""Verify a published release as an outsider would.  P3.5 / D10.

Fetches the LIVE site and checks it against what this commit builds. Nothing
here inspects the local _site as evidence of what visitors receive — that is
the difference between verifying a release and admiring a build.

THE NEGATIVE CONTROL (--negative-control) is not optional in the protocol.
It runs the same byte-identity check against a deliberately altered build and
MUST report failure. If the verification passes on something that should fail,
it would have passed on anything.

Usage (PowerShell):
    python tools\\verify_release.py --tag v1.0.0-rc.1
    python tools\\verify_release.py --tag v1.0.0-rc.1 --negative-control
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")     # defect D-13
sys.stderr.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "_site"
BASE = "https://mohdsaifhussain.github.io"
PAGES = ["/", "/projects/", "/experience/", "/certifications/", "/audit/"]

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
EXEMPT_DOMAINS = ("users.noreply.github.com",)
EXEMPT_LITERALS = ("noreply@anthropic.com",)


def fetch(url: str) -> tuple[int, str, dict]:
    req = urllib.request.Request(url, headers={"User-Agent": "release-verify"})
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            return r.status, r.read().decode("utf-8", "replace"), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, "", {}


def local_html(path: str) -> str | None:
    rel = "index.html" if path == "/" else path.strip("/") + "/index.html"
    f = SITE / rel
    return f.read_text(encoding="utf-8") if f.exists() else None


def verify(alter: bool) -> int:
    problems: list[tuple[str, str]] = []
    checked = 0

    print(f"Verifying {BASE}\n")

    # 1. HTTPS and reachability
    for path in PAGES:
        code, body, _h = fetch(BASE + path)
        checked += 1
        if code != 200:
            problems.append(("PAGE_NOT_200", f"{path} -> {code}"))
            continue

        # 2. Byte identity against what this commit builds.
        want = local_html(path)
        if want is None:
            problems.append(("LOCAL_MISSING", f"{path} not built locally"))
        else:
            if alter:
                # THE NEGATIVE CONTROL: compare against a build that differs by
                # one character. This MUST be detected.
                want = want.replace("</body>", "<!--x--></body>", 1)
            if body != want:
                problems.append(("CONTENT_MISMATCH",
                                 f"{path} deployed bytes differ from this commit's build"))

        # 3. CSP present and strict
        m = re.search(r'http-equiv="Content-Security-Policy" content="([^"]+)"', body)
        if not m:
            problems.append(("NO_CSP", path))
        elif "unsafe-inline" in m.group(1) or "unsafe-eval" in m.group(1):
            problems.append(("WEAK_CSP", path))

        # 4. C-33 on served pages
        for hit in EMAIL.finditer(body):
            addr = hit.group()
            if addr in EXEMPT_LITERALS or addr.rsplit("@", 1)[-1] in EXEMPT_DOMAINS:
                continue
            problems.append(("EMAIL_SERVED", f"{path} {addr}"))

    # 5. http -> https
    try:
        req = urllib.request.Request("http://mohdsaifhussain.github.io/",
                                     headers={"User-Agent": "release-verify"})
        opener = urllib.request.build_opener(NoRedirect)
        code = opener.open(req, timeout=30).status
        problems.append(("NO_HTTPS_REDIRECT", f"http returned {code}, expected a redirect"))
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 307, 308):
            loc = e.headers.get("Location", "")
            print(f"  http -> {e.code} {loc}")
            if not loc.startswith("https://"):
                problems.append(("NO_HTTPS_REDIRECT", loc))
        else:
            problems.append(("NO_HTTPS_REDIRECT", str(e.code)))

    # 6. /audit publishes measured values with protocol and environment
    _c, audit, _h = fetch(BASE + "/audit/")
    for needle, reason in [("MEASURED", "AUDIT_NOT_MEASURED"),
                           ("MEASUREMENT PROTOCOL", "AUDIT_NO_PROTOCOL"),
                           ("AGAINST", "AUDIT_NO_ENVIRONMENT")]:
        if needle not in audit:
            problems.append((reason, f"/audit lacks '{needle}'"))

    # 7. Evidence links resolve
    snap = json.loads((ROOT / "data/generated/github.json").read_text(encoding="utf-8"))
    for name, r in sorted(snap["repos"].items()):
        code, _b, _h = fetch(r["anchor_url"])
        checked += 1
        if code != 200:
            problems.append(("DEAD_EVIDENCE_LINK", f"{name} -> {code}"))

    print(f"\n  checks performed: {checked} fetches over {len(PAGES)} pages "
          f"+ {len(snap['repos'])} evidence links")

    if problems:
        print("\nRELEASE VERIFICATION FAILED")
        for reason, detail in problems:
            print(f"  REASON={reason}  {detail}")
        return 1

    print("\nRELEASE VERIFICATION OK — served bytes match this commit, HTTPS "
          "enforced, CSP strict, no contact data served, evidence links live")
    return 0


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--negative-control", action="store_true",
                    help="verify against a deliberately altered build; MUST fail")
    args = ap.parse_args()

    if args.negative_control:
        print("NEGATIVE CONTROL — this run MUST report failure.\n"
              "If it passes, the positive verification proved nothing.\n")
        rc = verify(alter=True)
        if rc == 0:
            print("\nNEGATIVE CONTROL DID NOT FAIL — verification is worthless. "
                  "STOP THE RELEASE.")
            return 1
        print("\nNEGATIVE CONTROL BEHAVED CORRECTLY: the altered build was "
              "detected, so the positive verification discriminates.")
        return 0

    return verify(alter=False)


if __name__ == "__main__":
    raise SystemExit(main())
