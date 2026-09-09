#!/usr/bin/env bash
# verify.sh — deterministic canonical-verification gate for a repository.
#
# Runs format -> lint -> typecheck -> test in order, fail-fast, streaming output,
# then prints an exact "what ran / what passed / what did not run" summary.
#
# The `automated-testing-workflow` skill owns the JUDGMENT (which scope for which risk,
# how to diagnose a failure, modification authority). This script only EXECUTES the gate.
#
# Provenance: the sequential fail-fast gate pattern is adapted from the OpenAI Agents SDK
# skill `code-change-verification` (github.com/openai/openai-agents-python, .agents/skills,
# MIT). No upstream code was copied.
#
# Configuration (first match wins):
#   1. A repo-local `verify.config` file (KEY=command per line) next to the repo root, or
#      pointed at by $VERIFY_CONFIG. Keys: format, lint, typecheck, test, setup.
#      Lines starting with # and blank lines are ignored. Empty value = skip that stage.
#   2. Auto-detection for common stacks (npm/pnpm/yarn, python, cargo, go).
#
# Usage:
#   verify.sh [--stage format,lint,typecheck,test] [--list] [--help]
#   VERIFY_CONFIG=path/to/verify.config verify.sh
set -uo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
STAGES="format lint typecheck test"
ONLY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --help|-h)
      sed -n '2,30p' "$0"; exit 0 ;;
    --list) LIST=1 ;;
    --stage) ONLY="${2//,/ }"; shift ;;
    --stage=*) ONLY="${1#*=}"; ONLY="${ONLY//,/ }" ;;
    *) echo "verify.sh: unknown arg: $1" >&2; exit 2 ;;
  esac
  shift
done

# --- resolve commands -------------------------------------------------------------
declare -A CMD
CONFIG="${VERIFY_CONFIG:-$ROOT/verify.config}"
if [ -f "$CONFIG" ]; then
  SRC="verify.config ($CONFIG)"
  while IFS= read -r line; do
    case "$line" in ''|\#*) continue ;; esac
    key="${line%%=*}"; val="${line#*=}"
    key="$(echo "$key" | tr -d '[:space:]')"
    CMD[$key]="$val"
  done < "$CONFIG"
else
  SRC="auto-detection"
  if [ -f "$ROOT/package.json" ]; then
    PM=npm
    [ -f "$ROOT/pnpm-lock.yaml" ] && PM=pnpm
    [ -f "$ROOT/yarn.lock" ] && PM=yarn
    has() { grep -q "\"$1\"" "$ROOT/package.json"; }
    RUN="$PM run"; [ "$PM" = npm ] && RUN="npm run"
    has format    && CMD[format]="$RUN format"
    has lint      && CMD[lint]="$RUN lint"
    { has typecheck && CMD[typecheck]="$RUN typecheck"; } || { has build && CMD[typecheck]="$RUN build"; }
    has test      && CMD[test]="$RUN test"
    CMD[setup]="${CMD[setup]:-$PM install}"
  elif [ -f "$ROOT/pyproject.toml" ] || [ -f "$ROOT/setup.cfg" ] || [ -f "$ROOT/requirements.txt" ]; then
    command -v ruff    >/dev/null 2>&1 && { CMD[format]="ruff format --check ."; CMD[lint]="ruff check ."; }
    command -v mypy    >/dev/null 2>&1 && CMD[typecheck]="mypy ."
    command -v pyright >/dev/null 2>&1 && CMD[typecheck]="pyright"
    command -v pytest  >/dev/null 2>&1 && CMD[test]="pytest -q"
  elif [ -f "$ROOT/Cargo.toml" ]; then
    CMD[format]="cargo fmt --check"; CMD[lint]="cargo clippy -- -D warnings"
    CMD[typecheck]="cargo check"; CMD[test]="cargo test"
  elif [ -f "$ROOT/go.mod" ]; then
    CMD[format]="gofmt -l ."; CMD[lint]="go vet ./..."; CMD[test]="go test ./..."
  fi
fi

if [ -n "${LIST:-}" ]; then
  echo "root:   $ROOT"
  echo "source: $SRC"
  for s in setup $STAGES; do printf '  %-10s %s\n' "$s" "${CMD[$s]:-<none>}"; done
  exit 0
fi

[ -n "$ONLY" ] && STAGES="$ONLY"

# --- run ------------------------------------------------------------------------
echo "verify.sh | root=$ROOT | commands from $SRC"
echo "stages: $STAGES"
echo

declare -A RESULT
FAILED=""
for s in $STAGES; do
  c="${CMD[$s]:-}"
  if [ -z "$c" ]; then RESULT[$s]="skip (no command)"; echo "== $s: SKIP (no command configured)"; echo; continue; fi
  echo "== $s: $c"
  ( cd "$ROOT" && eval "$c" )
  rc=$?
  if [ $rc -eq 0 ]; then RESULT[$s]="pass"; echo "== $s: PASS"; else RESULT[$s]="FAIL (exit $rc)"; FAILED="$s"; echo "== $s: FAIL (exit $rc)"; fi
  echo
  [ -n "$FAILED" ] && break
done

# --- summary ------------------------------------------------------------------------
echo "---------------- verify.sh summary ----------------"
for s in $STAGES; do printf '  %-10s %s\n' "$s" "${RESULT[$s]:-not run}"; done
if [ -n "$FAILED" ]; then
  NOTRUN=""
  seen=0
  for s in $STAGES; do
    [ "$s" = "$FAILED" ] && seen=1 && continue
    [ $seen -eq 1 ] && NOTRUN="$NOTRUN $s"
  done
  [ -n "$NOTRUN" ] && echo "  did not run:$NOTRUN (stopped at first failure)"
  echo "RESULT: FAIL at '$FAILED'"
  exit 1
fi
echo "RESULT: PASS"
