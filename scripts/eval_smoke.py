#!/usr/bin/env python3
"""Run eval cases: call ask() and save markdown for manual review."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.assistant import ask  # noqa: E402
from src.i18n import Locale  # noqa: E402
from src.models import PatientContext  # noqa: E402

CASES_FILE = PROJECT_ROOT / "data" / "eval" / "cases.yaml"
RUNS_DIR = PROJECT_ROOT / "data" / "eval" / "runs"


def _patient_from_case(case: dict) -> PatientContext:
    return PatientContext(
        treatment_types=case.get("treatment") or [],
        cycle_day=case.get("cycle_day"),
        on_corticosteroids_today=bool(case.get("corticosteroids")),
        comorbidities=case.get("comorbidity") or [],
        weight_trend=case.get("weight_trend", "unknown"),
        glucose=case.get("glucose", "unknown"),
        symptoms_today=case.get("symptoms") or [],
        dietary_restrictions=case.get("dietary_restrictions") or [],
    )


def run_eval(case_ids: list[str] | None = None, dry_run: bool = False) -> int:
    with CASES_FILE.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    cases = data.get("cases", [])

    if case_ids:
        cases = [c for c in cases if c.get("id") in case_ids]
        if not cases:
            print(f"No matching cases for: {case_ids}", file=sys.stderr)
            return 1

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = RUNS_DIR / stamp
    run_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for case in cases:
        cid = case["id"]
        patient = _patient_from_case(case)
        expected = case.get("expect_priority")
        actual = patient.derive_priority()

        if expected and actual != expected:
            print(f"[FAIL] {cid}: priority {actual} != expected {expected}")
            failures += 1
        else:
            print(f"[OK]   {cid}: priority {actual}")

        if dry_run:
            continue

        locale: Locale = case.get("locale", "bg")
        if locale == "auto":
            locale = "bg"

        try:
            response = ask(case["question"], locale=locale, patient=patient)
            md = response.render_markdown()
            header = (
                f"<!-- case: {cid} -->\n"
                f"<!-- expect_priority: {expected} -->\n"
                f"<!-- notes: {case.get('notes', '')} -->\n\n"
            )
            out_path = run_dir / f"{cid}.md"
            out_path.write_text(header + md, encoding="utf-8")
            print(f"       saved {out_path.relative_to(PROJECT_ROOT)}")
        except Exception as exc:
            print(f"[ERROR] {cid}: {exc}", file=sys.stderr)
            failures += 1

    print(f"\nRun directory: {run_dir.relative_to(PROJECT_ROOT)}")
    return 1 if failures else 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Eval smoke test for onco-nutrition")
    parser.add_argument(
        "--cases",
        nargs="+",
        help="Run only these case ids (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only check derive_priority, do not call LLM",
    )
    args = parser.parse_args()
    sys.exit(run_eval(case_ids=args.cases, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
