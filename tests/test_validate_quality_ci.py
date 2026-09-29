from __future__ import annotations

import json
import time
from pathlib import Path

from scripts.validate_quality_ci import validate_junit, validate_quality_report


def _write_quality_reports(tmp_path: Path) -> tuple[Path, Path, float, str, str]:
    base = "b" * 40
    head = "a" * 40
    checks = [
        {"name": name, "findings": [], "error": "", "note": "", "notices": []}
        for name in ("tamper", "py/form", "crap/tools", "doc", "secret", "tests", "cov/diff")
    ]
    report_path = tmp_path / "check.json"
    report_path.write_text(json.dumps({"checks": checks, "bypasses": []}), encoding="utf-8")
    markdown_path = tmp_path / "check.md"
    markdown_path.write_text(
        f"# Quality report now\nrepo fixture @ {head[:7]}, scope since {base}, base {base}\n"
        "tests: touched run exit 0, failed 0, lcov /tmp/coverage.info (removed after verdict)\n",
        encoding="utf-8",
    )
    return report_path, markdown_path, time.time() - 1, base, head


def test_quality_report_requires_fresh_complete_touched_run(tmp_path: Path) -> None:
    report, markdown, started_at, base, head = _write_quality_reports(tmp_path)
    assert validate_quality_report(report, markdown, started_at, base, head, 0, True) == []


def test_docs_only_report_does_not_require_python_source_checks(tmp_path: Path) -> None:
    report, markdown, started_at, base, head = _write_quality_reports(tmp_path)
    data = json.loads(report.read_text(encoding="utf-8"))
    data["checks"] = [
        check for check in data["checks"] if check["name"] not in {"py/form", "crap/tools"}
    ]
    report.write_text(json.dumps(data), encoding="utf-8")
    markdown.write_text(
        f"# Quality report now\nrepo fixture @ {head[:7]}, scope docs-only, base {base}\n",
        encoding="utf-8",
    )
    assert validate_quality_report(
        report, markdown, started_at, base, head, 0, docs_only_change=True
    ) == []


def test_quality_report_rejects_required_skip_even_on_zero_exit(tmp_path: Path) -> None:
    report, markdown, started_at, base, head = _write_quality_reports(tmp_path)
    data = json.loads(report.read_text(encoding="utf-8"))
    data["checks"][0]["notices"] = ["not run: scanner unavailable"]
    report.write_text(json.dumps(data), encoding="utf-8")
    assert "was not run" in " ".join(
        validate_quality_report(report, markdown, started_at, base, head, 0, True)
    )


def test_quality_report_rejects_stale_report(tmp_path: Path) -> None:
    report, markdown, _, base, head = _write_quality_reports(tmp_path)
    started_at = time.time() + 60
    errors = validate_quality_report(report, markdown, started_at, base, head, 0, True)
    assert any("predates this run" in error for error in errors)


def test_quality_report_rejects_findings_despite_zero_exit(tmp_path: Path) -> None:
    report, markdown, started_at, base, head = _write_quality_reports(tmp_path)
    data = json.loads(report.read_text(encoding="utf-8"))
    data["checks"][1]["findings"] = [{"rule": "example"}]
    report.write_text(json.dumps(data), encoding="utf-8")
    assert "finding(s)" in " ".join(
        validate_quality_report(report, markdown, started_at, base, head, 0, True)
    )


def test_quality_report_inspects_artifact_even_when_command_is_red(tmp_path: Path) -> None:
    report, markdown, started_at, base, head = _write_quality_reports(tmp_path)
    data = json.loads(report.read_text(encoding="utf-8"))
    data["checks"][5]["findings"] = [{"rule": "tests/red"}]
    report.write_text(json.dumps(data), encoding="utf-8")
    markdown.write_text(
        f"# Quality report now\nrepo fixture @ {head[:7]}, scope since {base}, base {base}\n"
        "tests: touched run exit 1, failed 1, lcov /tmp/coverage.info\n",
        encoding="utf-8",
    )
    errors = validate_quality_report(report, markdown, started_at, base, head, 1, True)
    assert "command exited 1" in " ".join(errors)
    assert "finding(s)" in " ".join(errors)


def test_quality_report_rejects_unreviewed_policy_delta(tmp_path: Path) -> None:
    report, markdown, started_at, base, head = _write_quality_reports(tmp_path)
    data = json.loads(report.read_text(encoding="utf-8"))
    data["checks"][0]["note"] = "tamper/baseline-touched .quality.toml"
    report.write_text(json.dumps(data), encoding="utf-8")
    assert "protected-config baseline" in " ".join(
        validate_quality_report(report, markdown, started_at, base, head, 0, True)
    )


def test_quality_report_rejects_wrong_base(tmp_path: Path) -> None:
    report, markdown, started_at, _, head = _write_quality_reports(tmp_path)
    errors = validate_quality_report(report, markdown, started_at, "c" * 40, head, 0, True)
    assert any("explicit base and since SHA" in error for error in errors)


def test_junit_requires_executed_cases_and_no_failures(tmp_path: Path) -> None:
    report = tmp_path / "junit.xml"
    report.write_text(
        '<testsuites><testsuite><testcase name="ok"/><testcase name="skip"><skipped/></testcase></testsuite></testsuites>',
        encoding="utf-8",
    )
    assert validate_junit(report, time.time() - 1) == []
    report.write_text(
        '<testsuites><testsuite><testcase name="bad"><failure/></testcase></testsuite></testsuites>',
        encoding="utf-8",
    )
    assert "test failures" in " ".join(validate_junit(report, time.time() - 1))


def test_junit_rejects_zero_or_all_skipped_cases(tmp_path: Path) -> None:
    report = tmp_path / "junit.xml"
    report.write_text("<testsuites><testsuite tests='0'/></testsuites>", encoding="utf-8")
    assert "no executed test cases" in " ".join(validate_junit(report, time.time() - 1))
    report.write_text(
        '<testsuite><testcase name="skip"><skipped/></testcase></testsuite>',
        encoding="utf-8",
    )
    assert "only skipped" in " ".join(validate_junit(report, time.time() - 1))
