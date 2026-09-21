#!/usr/bin/env bash
# Ralph Loop runner - POSIX (macOS/Linux/WSL).
# Shipped adapter is Cursor CLI (`agent`). Other CLIs replace invoke_executor.
# Every iteration spawns a NEW executor process (fresh context).
# State between iterations lives only on disk (IMPLEMENTATION_PLAN.md,
# PROGRESS.md) and in this directory's git history.
#
# Usage:
#   cd my-ralph-project
#   ./loop.sh
#   MODEL=claude-opus-4-8-thinking-high MAX_ITERATIONS=1 ./loop.sh   # Gate 0 / irreversible step
#
# Env vars:
#   MODEL                    (default: claude-sonnet-5-thinking-high)
#   MAX_ITERATIONS            0 = unlimited, stop only on RALPH_STATUS (default: 0)
#   SLEEP_SECONDS             (default: 3)
#   MAX_CONSECUTIVE_FAILURES  (default: 3)
#   EXECUTOR                  shipped adapter is Cursor CLI; other CLIs replace
#                              invoke_executor (default: cursor)
#
# Requirements:
#   - Cursor CLI installed and logged in: `agent --version` works (`agent login` if not).
#     Install: curl https://cursor.com/install -fsS | bash
#   - git available in PATH

set -uo pipefail

MODEL="${MODEL:-claude-sonnet-5-thinking-high}"
MAX_ITERATIONS="${MAX_ITERATIONS:-0}"
SLEEP_SECONDS="${SLEEP_SECONDS:-3}"
MAX_CONSECUTIVE_FAILURES="${MAX_CONSECUTIVE_FAILURES:-3}"
EXECUTOR="${EXECUTOR:-cursor}"

RALPH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f "$RALPH_DIR/PROMPT.md" ]; then
  RALPH_DIR="$(pwd)"
fi
cd "$RALPH_DIR"

invoke_executor() {
  local prompt_text="$1"
  local log_file="$2"
  case "$EXECUTOR" in
    cursor)
      agent -p --force --trust --model "$MODEL" --output-format text "$prompt_text" 2>&1 | tee "$log_file"
      return "${PIPESTATUS[0]}"
      ;;
    *)
      echo "Unknown or unverified executor '$EXECUTOR'. Edit this function to wire it in - see SKILL.md 'Executor backends'." >&2
      return 1
      ;;
  esac
}

if [ "$EXECUTOR" = "cursor" ] && ! command -v agent >/dev/null 2>&1; then
  echo "Cursor CLI 'agent' not found in PATH. Install: curl https://cursor.com/install -fsS | bash" >&2
  exit 1
fi

if [ ! -d "$RALPH_DIR/.git" ]; then
  git init -q
  for f in "$RALPH_DIR"/*.md; do
    [ -e "$f" ] && git add "$(basename "$f")"
  done
  git commit -q -m "ralph: init harness" || true
  echo "Initialized git repo in $RALPH_DIR (for iteration audit trail)."
fi

mkdir -p "$RALPH_DIR/logs"

iteration=0
consecutive_failures=0

while true; do
  if [ "$MAX_ITERATIONS" -gt 0 ] && [ "$iteration" -ge "$MAX_ITERATIONS" ]; then
    echo "Reached iteration limit ($MAX_ITERATIONS). Stopping."
    break
  fi
  iteration=$((iteration + 1))

  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo ""
  echo "=== Ralph iteration $iteration | executor=$EXECUTOR model=$MODEL | $ts ==="

  prompt="$(cat "$RALPH_DIR/PROMPT.md")"
  log_file="$RALPH_DIR/logs/iteration_$(printf '%03d' "$iteration").log"

  invoke_executor "$prompt" "$log_file"
  exit_code=$?

  if [ "$exit_code" -ne 0 ]; then
    consecutive_failures=$((consecutive_failures + 1))
    echo "Executor exited with code $exit_code (failure $consecutive_failures of $MAX_CONSECUTIVE_FAILURES in a row)."
    if [ "$consecutive_failures" -ge "$MAX_CONSECUTIVE_FAILURES" ]; then
      echo "Too many consecutive executor failures. Stopping loop - check executor auth/setup."
      break
    fi
    sleep "$SLEEP_SECONDS"
    continue
  fi
  consecutive_failures=0

  last_status_line="$(grep '^RALPH_STATUS:' "$RALPH_DIR/PROGRESS.md" 2>/dev/null | tail -n 1 || true)"

  if [ -n "$last_status_line" ]; then
    echo "$last_status_line"
  else
    echo "Warning: executor did not append RALPH_STATUS to PROGRESS.md this iteration."
  fi

  git add -A
  git commit -q -m "ralph: iteration $iteration ($ts)" || true

  if echo "$last_status_line" | grep -Eq 'RALPH_STATUS:\s*(BLOCKED|DONE)'; then
    status="$(echo "$last_status_line" | sed -E 's/.*RALPH_STATUS:\s*([A-Z]+).*/\1/')"
    echo "Loop stopped: $status"
    break
  fi

  sleep "$SLEEP_SECONDS"
done

echo ""
echo "Ralph loop finished after $iteration iteration(s). See PROGRESS.md and logs/."
