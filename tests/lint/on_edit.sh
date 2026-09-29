#!/usr/bin/env bash
#
# PostToolUse hook: run the static lint the moment Python source is edited.
#
# Wire it up in .claude/settings.json (that directory is gitignored, so this
# script lives here and the config there stays one line):
#
#   { "hooks": { "PostToolUse": [ { "matcher": "Edit|Write|MultiEdit",
#       "hooks": [ { "type": "command",
#         "command": "wsl bash <repo>/tests/lint/on_edit.sh" } ] } ] } }
#
# Why only the lint and not the whole suite: this runs after *every* edit, so
# it has to cost about a second. The lint stage does, and it is the stage
# that catches what an editor cannot -- a renamed method leaves a file that
# compiles and crashes later. The rest of tests/run.sh belongs before a
# commit, not after a keystroke.
#
# Reads the hook payload on stdin and does nothing unless the edited file is
# Python in this project. Always exits 0 on files it does not care about.
#
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PY="${OA_PYTHON:-python3}"

RELEVANT="$("$PY" "$ROOT/tests/lint/_relevant.py" "$ROOT" 2>/dev/null || echo no)"

[ "$RELEVANT" = yes ] || exit 0

cd "$ROOT"
export OA_ROOT="$ROOT"
# One at a time, accumulating the codes. Grouping them as
# `{ a; b; }` returns only b's status, so a failure in the first check
# vanishes -- which made this hook pass while the lint was failing.
rc=0
out=""
for check in cross_class_calls singleton_calls; do
    this="$("$PY" "tests/lint/$check.py" 2>&1)" || rc=1
    out="$out$this
"
done
if [ $rc -ne 0 ]; then
    printf 'tests/lint found a call that will raise AttributeError:\n\n%s\n' \
        "$(printf '%s
' "$out" | grep -E '^   linea ')"
    exit 2      # non-zero is surfaced back as feedback
fi
exit 0
