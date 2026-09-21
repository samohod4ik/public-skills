"""Refuse writes against a live or production Throne install."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

RUNNING_MARKER = Path("config") / "logs" / "running.marker"
LIVE_GUARD_NAME = ".throne-live-do-not-edit"


def throne_process_running() -> bool | None:
    """True if live, False if definitely not, None if the probe failed."""
    return _throne_process_running()


def _throne_process_running() -> bool | None:
    """True if live, False if definitely not, None if the probe failed."""
    if os.name != "nt":
        return False
    try:
        completed = subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                "if (Get-Process Throne,ThroneCore -ErrorAction SilentlyContinue) { 'yes' }",
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return "yes" in (completed.stdout or "").lower() if completed.returncode == 0 else None


def live_reason(throne_dir: Path) -> str | None:
    marker = throne_dir / RUNNING_MARKER
    if marker.exists():
        return (
            f"Refusing {throne_dir}: {RUNNING_MARKER.as_posix()} exists. "
            "Throne is running or this is a live config tree."
        )
    if (throne_dir / LIVE_GUARD_NAME).exists():
        return (
            f"Refusing {throne_dir}: {LIVE_GUARD_NAME} is present. "
            "Use a disposable Throne copy in cloud CI/VM."
        )
    has_exe = (throne_dir / "Throne.exe").exists()
    probe = _throne_process_running()
    if has_exe and probe is True:
        return (
            f"Refusing {throne_dir}: Throne.exe/ThroneCore is running. "
            "Do not rewrite a live install from an agent session."
        )
    if has_exe and probe is None:
        return (
            f"Refusing {throne_dir}: could not probe Throne.exe/ThroneCore. "
            "Fail closed while Throne.exe is present."
        )
    return None


def assert_not_live(throne_dir: str | Path) -> Path:
    path = Path(throne_dir).expanduser()
    reason = live_reason(path)
    if reason:
        raise SystemExit(reason)
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--throne-dir",
        default=os.environ.get("THRONE_DIR", ""),
        help="Throne install folder to check (does not write).",
    )
    args = parser.parse_args(argv)
    if not args.throne_dir:
        print("THRONE_DIR / --throne-dir is empty (ok: nothing to refuse)", file=sys.stderr)
        return 0
    assert_not_live(args.throne_dir)
    print(f"OK: {args.throne_dir} is not a live production Throne tree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
