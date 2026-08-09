"""Run the gates behind /audit's A2 rows and record what they actually said.

DEFECT D-48 IS WHY THIS EXISTS.
/audit's A2 table carried eight charter-check rows, every one of them reading
"— AT DEPLOY", under a footnote promising that such cells "ARE MEASURED BY CI AT
PUBLISH TIME". No writer ever produced those eight keys. Nothing was measuring
them, and nothing ever had. The page under-reported its own posture for the
whole of v1.0.0 — the same class as D-37 (a published limitation that had
stopped being true), pointed the other way.

WHAT THIS TOOL DOES, AND WHAT IT DELIBERATELY DOES NOT
It runs the real gates — the same checkers and tests the deploy job runs — and
writes their exit codes to JSON for tools/write_audit.py to merge. It computes
nothing itself. A row with no honest producer is ABSENT from the output and
/audit renders that row's declared basis instead, never a check mark. That is
the same rule write_audit.py follows for scores (contract 3.1/3.2): a value with
no tool behind it is an absence, never a plausible-looking placeholder.

WHY IT LIVES IN THE MEASUREMENT JOB, NOT THE DEPLOY JOB
data/generated/audit.json has EXACTLY ONE writer (defect D-42:
measure-live.yml). The deploy job may not write it — two writers raced and a
test-server figure overwrote a real one. So the measurement job runs these gates
itself. They are deterministic over a checked-out tree, so running them there
gives the same answer the deploy job's copy gives for the same commit; the
commit they ran against is recorded in the output and shown on the page.

THE SELECTION-DRIFT GUARD
Three rows are backed by named tests selected with `pytest -k`. A `-k` filter
that stops matching does not fail — pytest exits 5 with "no tests ran", and a
naive reading of "no failures" would publish a PASS backed by nothing. That is
exactly defect D-32, where a loop over an empty list passed by asserting
nothing. So each pytest-backed gate declares how many tests it expects to
select, and a mismatch is a FAILURE (REASON=SELECTION_DRIFT), not a pass.

Usage (CI):
    python tools/gate_status.py --json-out gates.json
    python tools/gate_status.py --selftest
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as dt
import json
import pathlib
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")     # defect D-13
sys.stderr.reconfigure(encoding="utf-8")

ROOT = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable


@dataclasses.dataclass(frozen=True)
class Gate:
    """One /audit A2 row and the thing that actually decides it.

    key         matches the `key` field of the row in data/audit-spec.json
    conditions  the charter conditions the row cites, copied for the record
    producer    human-readable name of what ran, shown on the page
    cmd         the command whose exit code is the verdict
    expect      for pytest selections: how many tests must be selected
    """
    key: str
    conditions: str
    producer: str
    cmd: tuple[str, ...]
    expect: int | None = None


def _pytest(*names: str) -> tuple[str, ...]:
    # No -q here: pytest.ini already sets `-q -rs`, and passing a second -q
    # raises verbosity to double-quiet, which suppresses the summary line
    # entirely. The count is read from the JUnit XML rather than from stdout
    # for exactly that reason — stdout formatting is a presentation detail
    # that a config change can alter, the XML report is a stable contract.
    return (PY, "-m", "pytest", "-p", "no:cacheprovider",
            "-k", " or ".join(names))


# The map from /audit row -> the gate that actually runs it.
#
# ABSENT ON PURPOSE, and this is the honest part of D-48's fix:
#   interaction_qa (A2.5) — handoff §6 is a human observation. There is one
#       automated slice of it (test_evidence_layer_never_covers_the_links_column)
#       but "no hover layer blocks or overlaps another interactive element"
#       across every page was established by a person looking. /audit links the
#       dated record instead of claiming a machine measured it.
#   reduced_motion (A2.7) — "complete AND COHERENT with prefers-reduced-motion".
#       The mechanical half is now gated (check_animations.py, REASON=
#       MOTION_NOT_REDUCED, added in the same commit as this file). Whether the
#       page still makes sense with motion off is an observation, so this row
#       also links its dated record rather than showing a machine verdict.
GATES: tuple[Gate, ...] = (
    Gate("motion", "C-15", "tools/check_animations.py",
         (PY, "tools/check_animations.py")),
    Gate("scroll", "C-14", "tools/check_animations.py",
         (PY, "tools/check_animations.py")),
    Gate("c33", "C-33 + Amendments 1, 2", "tools/check_c33.py",
         (PY, "tools/check_c33.py")),
    Gate("no_third_party", "C-04, C-19, C-21",
         "tests: third-party resources, outbound allowlist, CSP",
         _pytest("test_no_third_party_resources_load",
                 "test_outbound_links_are_allowlisted",
                 "test_csp_present_and_strict",
                 "test_csp_omits_directives_meta_ignores"), expect=4),
    Gate("honesty", "C-27", "tests: verification marks and metrics basis",
         _pytest("test_verified_entries_render_a_check",
                 "test_pending_entries_never_render_a_check",
                 "test_some_page_carries_both_marks",
                 "test_metrics_basis_agrees_with_entries"), expect=4),
    Gate("anchored", "C-27, C-35", "build gate STAT_UNANCHORED + its controls",
         _pytest("test_real_projects_all_anchored",
                 "test_anchor_missing_refused"), expect=2),
)


def run_gate(gate: Gate) -> dict:
    """Run one gate. Its exit code is the verdict; nothing is inferred."""
    if gate.expect is None:
        r = subprocess.run(gate.cmd, cwd=ROOT, capture_output=True, text=True)
        status = "PASS" if r.returncode == 0 else "FAIL"
        return {"status": status, "producer": gate.producer,
                "conditions": gate.conditions, "detail": f"exit {r.returncode}"}

    with tempfile.TemporaryDirectory() as td:
        report = pathlib.Path(td) / "report.xml"
        r = subprocess.run(gate.cmd + ("--junit-xml", str(report)),
                           cwd=ROOT, capture_output=True, text=True)
        selected = failures = errors = skipped = 0
        if report.exists():
            root = ET.parse(report).getroot()
            suite = root.find("testsuite") if root.tag == "testsuites" else root
            if suite is not None:
                selected = int(suite.get("tests", 0))
                failures = int(suite.get("failures", 0))
                errors = int(suite.get("errors", 0))
                skipped = int(suite.get("skipped", 0))

    passed = selected - failures - errors - skipped
    detail = (f"{selected} selected, {passed} passed, {skipped} skipped, "
              f"{failures + errors} failed")
    status = "PASS"
    if selected != gate.expect:
        # D-32's failure mode: a selection that stopped selecting looks exactly
        # like a selection with nothing wrong. pytest exits 5 on "no tests ran",
        # and a naive "no failures" reading would publish a PASS backed by
        # nothing at all.
        status = "FAIL"
        detail += f"  REASON=SELECTION_DRIFT (expected {gate.expect})"
    elif failures or errors:
        status = "FAIL"
    # A skip is NOT a failure here — test_pending_entries_never_render_a_check
    # skips loudly and by design when no entry has pending metrics (D-32). It
    # is surfaced in `detail` and on the page rather than being absorbed into
    # a clean-looking pass.
    return {"status": status, "producer": gate.producer,
            "conditions": gate.conditions, "detail": detail,
            "skipped": skipped}


def commit_sha() -> str:
    r = subprocess.run(("git", "rev-parse", "HEAD"), cwd=ROOT,
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "unknown"


def run(json_out: pathlib.Path | None) -> int:
    results, failed = {}, []
    print("GATE STATUS — running the gates behind /audit's A2 rows\n")
    for gate in GATES:
        res = run_gate(gate)
        results[gate.key] = res
        if res["status"] != "PASS":
            failed.append(gate.key)
        print(f"  [{res['status']:<4}] {gate.key:<16} {gate.producer:<52} "
              f"{res['detail']}")

    absent = ("interaction_qa", "reduced_motion")
    print(f"\n  no machine producer, by design: {', '.join(absent)}")
    print("  those rows publish a dated human observation, not a check mark")

    now = dt.datetime.now(dt.timezone.utc)
    payload = {
        "_generated": ("Machine-written by tools/gate_status.py from real gate "
                       "exit codes. NEVER hand-edited. A row with no producer "
                       "is absent here and renders its declared basis on "
                       "/audit, never a verification mark."),
        "as_of": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "commit": commit_sha(),
        "results": results,
    }
    if json_out:
        json_out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8", newline="\n")
        print(f"\n  written to {json_out}")

    if failed:
        print(f"\nGATE STATUS FAILED — {', '.join(failed)}")
        return 1
    print(f"\nGATE STATUS OK — {len(results)} gates ran and passed "
          f"against commit {payload['commit'][:7]}")
    return 0


def selftest() -> int:
    """Prove the tool reports FAIL, and prove the drift guard bites.

    D-44: a guard verified only by its own passing is a decoration. Both
    failure paths are exercised here against synthetic gates, so "everything
    passed" is distinguishable from "nothing was checked".
    """
    ok = True
    print("SELFTEST — a failing gate must report FAIL, and an empty test "
          "selection must NOT report PASS\n")

    cases = [
        ("a gate that exits 0 reports PASS",
         Gate("x", "-", "true", (PY, "-c", "raise SystemExit(0)")), "PASS"),
        ("a gate that exits 1 reports FAIL",
         Gate("x", "-", "false", (PY, "-c", "raise SystemExit(1)")), "FAIL"),
        ("a pytest selection matching NOTHING reports FAIL, not PASS (D-32)",
         Gate("x", "-", "empty selection",
              _pytest("test_this_name_does_not_exist_anywhere"), expect=2), "FAIL"),
        ("a pytest selection matching FEWER than declared reports FAIL",
         Gate("x", "-", "short selection",
              _pytest("test_real_projects_all_anchored"), expect=2), "FAIL"),
        ("a pytest selection matching exactly its declared count reports PASS",
         Gate("x", "-", "exact selection",
              _pytest("test_real_projects_all_anchored"), expect=1), "PASS"),
    ]
    for label, gate, expected in cases:
        got = run_gate(gate)["status"]
        good = got == expected
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {label:<64} -> {got}")

    # The control that matters most: a test that genuinely FAILS must surface
    # as FAIL. Proven against a throwaway failing test rather than by reading
    # the code, because the whole point of D-44 is that a guard which has never
    # been seen to fail is not evidence of anything.
    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        (tmp / "test_deliberate_failure.py").write_text(
            "def test_deliberately_fails():\n    assert False\n", encoding="utf-8")
        # -c with an empty ini: pytest.ini's testpaths/addopts must not apply,
        # or this would collect the real suite instead of the one fake test.
        (tmp / "empty.ini").write_text("[pytest]\n", encoding="utf-8")
        got = run_gate(Gate("x", "-", "a genuinely failing test",
                            (PY, "-m", "pytest", "-c", str(tmp / "empty.ini"),
                             "-p", "no:cacheprovider", str(tmp)),
                            expect=1))
        good = got["status"] == "FAIL"
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] a genuinely failing test reports "
              f"FAIL{'':<26} -> {got['status']} ({got['detail']})")

    # Every key here must exist in audit-spec.json, or the page silently keeps
    # rendering "— AT DEPLOY" while this tool believes it filled the cell.
    spec = json.loads((ROOT / "data" / "audit-spec.json")
                      .read_text(encoding="utf-8"))
    spec_keys = {row["key"] for row in spec["a2_charter_checks"]}
    unknown = {g.key for g in GATES} - spec_keys
    good = not unknown
    ok = ok and good
    print(f"  [{'PASS' if good else 'FAIL'}] every gate key exists in "
          f"audit-spec.json{'' if good else f' — unknown: {unknown}'}")

    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json-out", type=pathlib.Path)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    return selftest() if args.selftest else run(args.json_out)


if __name__ == "__main__":
    raise SystemExit(main())
