#!/usr/bin/env bash
# Scaffold a new Ralph Loop project from this skill's templates.
#
# Usage:
#   ./init-ralph-project.sh /path/to/my-project "One-line description of the task"

set -euo pipefail

PROJECT_DIR="${1:?Usage: init-ralph-project.sh <project-dir> <project-name>}"
PROJECT_NAME="${2:?Usage: init-ralph-project.sh <project-dir> <project-name>}"

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATES_DIR="$SKILL_DIR/templates"

mkdir -p "$PROJECT_DIR/logs"

for file in AGENTS.md PROMPT.md IMPLEMENTATION_PLAN.md PROGRESS.md; do
  src="$TEMPLATES_DIR/$file.template"
  dst="$PROJECT_DIR/$file"
  if [ -e "$dst" ]; then
    echo "Skipping $file (already exists)"
    continue
  fi
  sed -e "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" -e "s|{{HARNESS_DIR}}|$PROJECT_DIR|g" "$src" > "$dst"
  echo "Created $dst"
done

cp "$SKILL_DIR/scripts/loop.sh" "$PROJECT_DIR/loop.sh"
cp "$SKILL_DIR/scripts/loop.ps1" "$PROJECT_DIR/loop.ps1"
chmod +x "$PROJECT_DIR/loop.sh"
echo "Copied loop.sh / loop.ps1"

[ -e "$PROJECT_DIR/.env" ] || echo "# Secrets for this Ralph project. Do not commit." > "$PROJECT_DIR/.env"
[ -e "$PROJECT_DIR/.gitignore" ] || printf '.env\nlogs/\n*.log\n' > "$PROJECT_DIR/.gitignore"

cat <<EOF

Next steps:
  1. Edit $PROJECT_DIR/AGENTS.md - fill in {{REAL_TARGET_ENV_PATH}} and any task-specific rules
  2. Edit $PROJECT_DIR/IMPLEMENTATION_PLAN.md - turn Phase placeholders into concrete checkboxes
  3. cd $PROJECT_DIR && ./loop.sh
EOF
