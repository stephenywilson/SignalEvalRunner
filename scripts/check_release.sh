#!/usr/bin/env bash
# Pre-release verification script for SignalEval Runner.
# Uses only mock/file providers — no external API calls, no API keys required.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DEMO_DATASET="$PROJECT_DIR/examples/datasets/demo.jsonl"
SAMPLE_PREDS="$PROJECT_DIR/examples/predictions/sample_predictions.jsonl"
IMPERFECT_PREDS="$PROJECT_DIR/examples/predictions/imperfect_predictions.jsonl"
RELEASE_VENV="/tmp/signalevalrunner-release-test"
MOCK_OUTPUT="/tmp/signalevalrunner-mock-predictions.jsonl"
REPORT_OUTPUT="/tmp/signalevalrunner-report.md"
SCORE_JSON_OUTPUT="/tmp/signalevalrunner-metrics.json"

pass() { echo "  PASS: $*"; }
fail() { echo "  FAIL: $*" >&2; exit 1; }

echo "========================================"
echo "  SignalEval Runner — Release Check"
echo "  Version: $(python3 -c 'import importlib.metadata; print(importlib.metadata.version("signalevalrunner"))' 2>/dev/null || echo '(not installed yet)')"
echo "========================================"
echo ""

# ── 1. Python version ─────────────────────────────────────────────────────────
echo "[1] Python version"
python3 --version
python3 -c "import sys; assert sys.version_info >= (3,10), f'Python 3.10+ required, got {sys.version}'"
pass "Python 3.10+"

# ── 2. Fresh venv install ──────────────────────────────────────────────────────
echo ""
echo "[2] Fresh venv install (pip install .)"
rm -rf "$RELEASE_VENV"
python3 -m venv "$RELEASE_VENV"
# shellcheck disable=SC1090
source "$RELEASE_VENV/bin/activate"
pip install "$PROJECT_DIR" -q
pass "pip install . succeeded"

# ── 3. CLI entrypoint ─────────────────────────────────────────────────────────
echo ""
echo "[3] CLI entrypoint"
signaleval --help > /dev/null
pass "signaleval --help"

# ── 4. Version output ─────────────────────────────────────────────────────────
echo ""
echo "[4] Version output"
VERSION_OUT=$(signaleval --version 2>&1)
echo "  Output: $VERSION_OUT"
echo "$VERSION_OUT" | grep -q "SignalEval Runner" || fail "--version does not contain 'SignalEval Runner'"
echo "$VERSION_OUT" | grep -qE "[0-9]+\.[0-9]+\.[0-9]+" || fail "--version does not contain a version number"
pass "signaleval --version: $VERSION_OUT"

# ── 5. python -m signaleval ───────────────────────────────────────────────────
echo ""
echo "[5] python -m signaleval --help"
python -m signaleval --help > /dev/null
pass "python -m signaleval --help"

# ── 6. init ───────────────────────────────────────────────────────────────────
echo ""
echo "[6] signaleval init"
INIT_DIR="$(mktemp -d)"
cd "$INIT_DIR"
signaleval init
test -f .signaleval/config.json || fail "config.json not created"
test -d .signaleval/outputs    || fail "outputs/ not created"
test -d .signaleval/reports    || fail "reports/ not created"
signaleval init                  # should not crash
signaleval init --force
pass "signaleval init (including second run and --force)"
cd "$PROJECT_DIR"

# ── 7. validate ───────────────────────────────────────────────────────────────
echo ""
echo "[7] signaleval validate"
signaleval validate --dataset "$DEMO_DATASET"
pass "validate demo dataset"

# ── 8. run (mock) ─────────────────────────────────────────────────────────────
echo ""
echo "[8] signaleval run --provider mock"
signaleval run \
  --dataset "$DEMO_DATASET" \
  --provider mock \
  --output "$MOCK_OUTPUT"
test -f "$MOCK_OUTPUT" || fail "mock output not created"
LINES=$(wc -l < "$MOCK_OUTPUT" | tr -d ' ')
test "$LINES" -eq 20 || fail "expected 20 lines, got $LINES"
pass "mock run produced $LINES predictions"

# ── 9. score (sample) ─────────────────────────────────────────────────────────
echo ""
echo "[9] signaleval score (sample predictions)"
signaleval score \
  --dataset "$DEMO_DATASET" \
  --predictions "$SAMPLE_PREDS" \
  --json-output "$SCORE_JSON_OUTPUT"
test -f "$SCORE_JSON_OUTPUT" || fail "score JSON output not created"
MACRO=$(python3 -c "import json; d=json.load(open('$SCORE_JSON_OUTPUT')); print(round(d['macro_score']*100,1))")
echo "  Macro score (sample): ${MACRO}%"
pass "score command with --json-output"

# ── 10. score (imperfect) ─────────────────────────────────────────────────────
echo ""
echo "[10] signaleval score (imperfect predictions)"
signaleval score \
  --dataset "$DEMO_DATASET" \
  --predictions "$IMPERFECT_PREDS"
pass "score command with imperfect predictions"

# ── 11. report ────────────────────────────────────────────────────────────────
echo ""
echo "[11] signaleval report"
signaleval report \
  --dataset "$DEMO_DATASET" \
  --predictions "$SAMPLE_PREDS" \
  --output "$REPORT_OUTPUT"
test -f "$REPORT_OUTPUT"                                  || fail "report not created"
grep -q "SignalEval Report"   "$REPORT_OUTPUT"            || fail "report missing header"
grep -q "Not financial advice" "$REPORT_OUTPUT"           || fail "report missing disclaimer"
grep -q "Research only"       "$REPORT_OUTPUT"            || fail "report missing research-only note"
# Confirm no absolute local paths leaked into the report
grep -q "/Users/" "$REPORT_OUTPUT" && fail "report contains absolute local path" || true
pass "report created and validated"

# ── 12. providers listing ─────────────────────────────────────────────────────
echo ""
echo "[12] signaleval providers"
PROVIDERS_OUT=$(signaleval providers)
echo "$PROVIDERS_OUT" | grep -q "mock"      || fail "mock not listed"
echo "$PROVIDERS_OUT" | grep -q "file"      || fail "file not listed"
echo "$PROVIDERS_OUT" | grep -q "ollama"    || fail "ollama not listed"
echo "$PROVIDERS_OUT" | grep -q "openai"    || fail "openai not listed"
echo "$PROVIDERS_OUT" | grep -q "anthropic" || fail "anthropic not listed"
pass "all 5 providers listed"

# ── 13. Security checks ───────────────────────────────────────────────────────
echo ""
echo "[13] Security: no API keys in source"
cd "$PROJECT_DIR"
if grep -r "sk-\|OPENAI_API_KEY\s*=\s*['\"].\|ANTHROPIC_API_KEY\s*=\s*['\"]." \
      signaleval/ --include="*.py" -l 2>/dev/null | grep -v ".pyc"; then
  fail "API key pattern found in source"
fi
pass "no hardcoded API keys in source"

# ── 14. No private paths ──────────────────────────────────────────────────────
echo ""
echo "[14] Security: no private absolute paths in source"
if grep -r "/Users/" signaleval/ --include="*.py" -l 2>/dev/null; then
  fail "private absolute path found in source"
fi
pass "no private paths in source"

# ── Cleanup ───────────────────────────────────────────────────────────────────
deactivate 2>/dev/null || true
rm -rf "$RELEASE_VENV" "$INIT_DIR"

echo ""
echo "========================================"
echo "  Release check PASSED"
echo "========================================"
