#!/usr/bin/env python3
"""Validate fresh Code Quality and pytest reports produced by the public CI job."""
from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

BASE_REQUIRED = ("tamper", "py/form", "crap/tools", "doc", "secret")
DOCS_ONLY_REQUIRED = ("tamper", "doc", "secret")
SOURCE_TEST_REQUIRED = ("tests", "cov/diff")


def _fresh_file(path: Path, started_at: float, label: str) -> list[str]:
    if not path.is_file():
        return [f"{label} report is missing: {path}"]
    if path.stat().st_size == 0:
        return [f"{label} report is empty: {path}"]
    if path.stat().st_mtime + 0.001 < started_at:
        return [f"{label} report predates this run: {path}"]
    return []


def validate_junit(path: Path, started_at: float) -> list[str]:
    errors = _fresh_file(path, started_at, "JUnit")
    if errors:
        return errors
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError) as exc:
        return [f"JUnit report is malformed: {exc}"]

    cases = list(root.iter("testcase"))
    if not cases:
        return ["JUnit report has no executed test cases"]
    executed = [case for case in cases if case.find("skipped") is None]
    if not executed:
        return ["JUnit report contains only skipped test cases"]
    if any(case.find("failure") is not None for case in cases):
        errors.append("JUnit report contains test failures")
    if any(case.find("error") is not None for case in cases):
        errors.append("JUnit report contains test errors")
    return errors


def _check_not_run(check: dict[str, Any]) -> bool:
    detail = " ".join(
        [str(check.get("note", "")), *(str(item) for item in check.get("notices", []))]
    )
    return bool(re.search(r"\bnot[ -]run\b|\bskipped\b", detail, re.IGNORECASE))


def validate_quality_report(
    report_path: Path,
    markdown_path: Path,
    started_at: float,
    expected_base: str,
    expected_head: str,
    quality_exit: int,
    source_test_change: bool = False,
    docs_only_change: bool = False,
    bootstrap_config_only: bool = False,
) -> list[str]:
    errors = _fresh_file(report_path, started_at, "Code Quality JSON")
    errors.extend(_fresh_file(markdown_path, started_at, "Code Quality Markdown"))
    if errors:
        return errors
    if quality_exit != 0:
        errors.append(f"Code Quality command exited {quality_exit}")

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
        markdown = markdown_path.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"Code Quality report is malformed or unreadable: {exc}")
        return errors
    if not isinstance(report, dict) or not isinstance(report.get("checks"), list):
        errors.append("Code Quality JSON has no checks array")
        return errors

    if f"@ {expected_head[:7]}," not in markdown:
        errors.append("Code Quality Markdown does not identify the exact candidate head")
    expected_scope = (
        f"scope docs-only, base {expected_base}"
        if docs_only_change
        else f"scope since {expected_base}, base {expected_base}"
    )
    if expected_scope not in markdown:
        errors.append("Code Quality Markdown does not show the explicit base and since SHA")

    by_name: dict[str, dict[str, Any]] = {}
    for check in report["checks"]:
        if not isinstance(check, dict) or not isinstance(check.get("name"), str):
            errors.append("Code Quality checks array contains a malformed entry")
            continue
        name = check["name"]
        if name in by_name:
            errors.append(f"Code Quality report duplicates check {name!r}")
            continue
        by_name[name] = check
        findings = check.get("findings")
        if not isinstance(findings, list):
            errors.append(f"Code Quality check {name!r} has no findings array")
        elif findings:
            errors.append(f"Code Quality check {name!r} has {len(findings)} finding(s)")
        error = check.get("error")
        if error not in (None, ""):
            errors.append(f"Code Quality check {name!r} reports an error: {error}")

    required = list(DOCS_ONLY_REQUIRED if docs_only_change else BASE_REQUIRED)
    if source_test_change:
        required.extend(SOURCE_TEST_REQUIRED)
    missing = [name for name in required if name not in by_name]
    if missing:
        errors.append(f"Code Quality report is missing required checks: {', '.join(missing)}")
    for name in required:
        check = by_name.get(name)
        if check is not None and _check_not_run(check):
            errors.append(f"required Code Quality check {name!r} was not run")

    tamper = by_name.get("tamper", {})
    tamper_details = " ".join(
        [str(tamper.get("note", "")), *(str(item) for item in tamper.get("notices", []))]
    )
    if not bootstrap_config_only and "baseline-touched" in tamper_details:
        errors.append("candidate report contains an unsuppressed protected-config baseline note")

    bypasses = report.get("bypasses", [])
    if bypasses:
        errors.append("Code Quality report contains bypass notices")

    if (
        source_test_change
        and not bootstrap_config_only
        and not re.search(
            r"^tests: touched run exit 0, failed 0, lcov .+",
            markdown,
            re.MULTILINE,
        )
    ):
        errors.append("Code Quality report does not prove a successful fresh touched-test run")

    if (
        bootstrap_config_only
        and ("baseline-touched" not in tamper_details or ".quality.toml" not in tamper_details)
    ):
        errors.append("bootstrap report must retain the intentional protected-config baseline note")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    junit = subparsers.add_parser("junit", help="validate a fresh pytest JUnit report")
    junit.add_argument("--report", type=Path, required=True)
    junit.add_argument("--started-at", type=float, required=True)

    quality = subparsers.add_parser("quality", help="validate Code Quality reports")
    quality.add_argument("--json-report", type=Path, required=True)
    quality.add_argument("--markdown-report", type=Path, required=True)
    quality.add_argument("--started-at", type=float, required=True)
    quality.add_argument("--base", required=True)
    quality.add_argument("--head", required=True)
    quality.add_argument("--exit-code", type=int, required=True)
    quality.add_argument("--source-test-change", action="store_true")
    quality.add_argument("--docs-only-change", action="store_true")
    quality.add_argument("--bootstrap-config-only", action="store_true")

    args = parser.parse_args()
    if args.command == "junit":
        errors = validate_junit(args.report, args.started_at)
    else:
        errors = validate_quality_report(
            args.json_report,
            args.markdown_report,
            args.started_at,
            args.base,
            args.head,
            args.exit_code,
            args.source_test_change,
            args.docs_only_change,
            args.bootstrap_config_only,
        )
    if errors:
        for error in errors:
            print(f"FAIL {error}")
        return 1
    print(f"PASS {args.command} report validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
