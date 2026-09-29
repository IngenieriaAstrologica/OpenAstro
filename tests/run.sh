#!/usr/bin/env bash
#
# The whole verification suite. Exits 0 only if every stage passes.
#
#   bash tests/run.sh            everything
#   bash tests/run.sh lint       one stage (lint|engine|render|dialog|e2e)
#
# Run it from anywhere; it locates the repository itself.
#
# Two things here are not decoration:
#
#   HOME is redirected to a throwaway directory before anything runs.
#   openAstroCfg() creates and writes ~/.openastro.org/ -- astrodb.sql holds
#   the user's saved charts and settings. A harness that builds it with the
#   real HOME edits live user data, and the .bak files next to that database
#   say this has already gone wrong at least once. Nothing in this suite may
#   ever see the real HOME.
#
#   GTK needs WAYLAND_DISPLAY unset, not just DISPLAY. Under WSLg, GDK
#   prefers Wayland and quietly ignores the DISPLAY that xvfb-run sets, so
#   the window lands on the real desktop instead of the virtual one.
#
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export OA_ROOT="$ROOT"
cd "$ROOT"

PY="${OA_PYTHON:-python3}"

# Resolve the user site-packages BEFORE HOME moves. pyswisseph is installed
# per-user (pip --user), so it lives under the real $HOME -- and Python
# derives that location from HOME at startup. Redirecting HOME without this
# line makes every engine test die with "No module named 'swisseph'", which
# looks like a missing dependency and is not.
USER_SITE="$("$PY" -m site --user-site 2>/dev/null || true)"

# Same story for the Swiss Ephemeris data. The .se1 files are not in the
# repository and /usr/share/swisseph is empty here; they live in the real
# ~/.openastro.org/swiss_ephemeris/, put there by openAstroCfg on first run.
# They are static astronomical data, not user data, so the throwaway home
# gets a symlink to them -- reads go to the real files, writes stay inside
# the sandbox. Point OA_EPHE somewhere else to override.
REAL_HOME="${HOME}"
OA_EPHE="${OA_EPHE:-$REAL_HOME/.openastro.org/swiss_ephemeris}"

OA_HOME="$(mktemp -d "${TMPDIR:-/tmp}/oa-tests-home.XXXXXX")"
export HOME="$OA_HOME"
export PYTHONPATH="$ROOT${USER_SITE:+:$USER_SITE}"
export OA_OUT="$(mktemp -d "${TMPDIR:-/tmp}/oa-tests-out.XXXXXX")"
if [ -d "$OA_EPHE" ]; then
    mkdir -p "$OA_HOME/.openastro.org"
    ln -s "$OA_EPHE" "$OA_HOME/.openastro.org/swiss_ephemeris"
else
    printf 'warning: no ephemeris at %s -- engine tests will fail
' "$OA_EPHE"
fi

# Restores the exit status explicitly. bash 5.2 preserves it through a plain
# EXIT trap on its own -- measured, not assumed -- so this is belt and braces
# for other shells, not a fix for anything observed here.
cleanup() { rc=$?; rm -rf "$OA_HOME" "$OA_OUT"; exit $rc; }
trap cleanup EXIT

# headless GTK: -u WAYLAND_DISPLAY is what makes xvfb actually take effect
GUI=(env -u WAYLAND_DISPLAY -u DISPLAY GDK_BACKEND=x11 xvfb-run -a "$PY")

WANT="${1:-all}"
PASS=0; FAIL=0; FAILED=()

run_one() {                      # run_one <label> <runner...> <script>
    local label="$1"; shift
    local out rc
    out="$("$@" 2>&1)"; rc=$?
    if [ $rc -eq 0 ]; then
        PASS=$((PASS+1)); printf '  ok    %s\n' "$label"
    else
        FAIL=$((FAIL+1)); FAILED+=("$label")
        printf '  FAIL  %s  (exit %d)\n' "$label" "$rc"
        printf '%s\n' "$out" | tail -20 | sed 's/^/        /'
    fi
}

stage() {                        # stage <name> <dir> <gui?>
    local name="$1" dir="$2" gui="$3"
    [ "$WANT" = all ] || [ "$WANT" = "$name" ] || return 0
    [ -d "$dir" ] || return 0
    local scripts=("$dir"/*.py)
    [ -e "${scripts[0]}" ] || return 0
    printf '\n%s\n' "== $name =="
    for s in "${scripts[@]}"; do
        case "$(basename "$s")" in _*) continue;; esac
        if [ "$gui" = gui ]; then
            run_one "$(basename "$s")" "${GUI[@]}" "$s"
        else
            run_one "$(basename "$s")" "$PY" "$s"
        fi
    done
}

printf 'repo   %s\n' "$ROOT"
printf 'HOME   %s  (throwaway)\n' "$HOME"

stage lint   tests/lint   cpu
stage engine tests/engine cpu
stage render tests/render gui
stage dialog tests/dialog gui
stage e2e    tests/e2e    gui

# The suite is worthless if it wrote to the real home, so prove it did not.
if [ -e "$HOME/.openastro.org" ]; then
    printf '\n  (openAstroCfg created %s -- as intended, inside the throwaway)\n' \
        "$HOME/.openastro.org"
fi
REAL_HOME="$(getent passwd "$(id -u)" 2>/dev/null | cut -d: -f6)"
if [ -n "$REAL_HOME" ] && [ "$REAL_HOME" != "$OA_HOME" ]; then
    if [ -e "$REAL_HOME/.openastro.org/astrodb.sql" ]; then
        NOW=$(date -r "$REAL_HOME/.openastro.org/astrodb.sql" +%s 2>/dev/null || echo 0)
        if [ -n "${OA_DB_MTIME:-}" ] && [ "$NOW" != "$OA_DB_MTIME" ]; then
            printf '\n  ERROR: the real astrodb.sql was modified by this run\n'
            FAIL=$((FAIL+1)); FAILED+=("touched the real HOME")
        fi
    fi
fi

printf '\n%d passed, %d failed\n' "$PASS" "$FAIL"
if [ "$FAIL" -ne 0 ]; then
    printf 'failing: %s\n' "${FAILED[*]}"
    exit 1
fi
exit 0
