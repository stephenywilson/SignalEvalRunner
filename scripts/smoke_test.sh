#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DEMO_DATASET="$PROJECT_DIR/examples/datasets/demo.jsonl"
SAMPLE_PREDS="$PROJECT_DIR/examples/predictions/sample_predictions.jsonl"

echo "========================================"
echo "  SignalEval Runner — Smoke Test"
echo "========================================"
echo "Project: $PROJECT_DIR"
echo ""

cd "$PROJECT_DIR"

# Check Python version
python3 --version
python3 -c "import sys; assert sys.version_info >= (3,10), f'Python 3.10+ required, got {sys.version}'"
echo "Python version OK"

# Verify signaleval is installed and importable
python3 -c "import signaleval; print(f'signaleval {signaleval.__version__} imported OK')"

# --help
echo ""
echo "--- signaleval --help ---"
signaleval --help

# providers
echo ""
echo "--- signaleval providers ---"
signaleval providers

# init (use temp dir to avoid polluting project)
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT
cd "$TMPDIR"
echo ""
echo "--- signaleval init (in $TMPDIR) ---"
signaleval init
test -f .signaleval/config.json && echo "config.json created OK"
test -d .signaleval/outputs && echo "outputs/ created OK"
test -d .signaleval/reports && echo "reports/ created OK"

# init again without --force should not overwrite
signaleval init && echo "second init without --force OK (no crash)"

# init with --force
signaleval init --force && echo "--force init OK"

cd "$PROJECT_DIR"

# validate
echo ""
echo "--- signaleval validate ---"
signaleval validate --dataset "$DEMO_DATASET"

# run with mock provider
echo ""
echo "--- signaleval run (mock provider) ---"
MOCK_OUTPUT="$TMPDIR/mock_predictions.jsonl"
signaleval run \
  --dataset "$DEMO_DATASET" \
  --provider mock \
  --output "$MOCK_OUTPUT"
test -f "$MOCK_OUTPUT" && echo "mock output file created OK"
MOCK_LINES=$(wc -l < "$MOCK_OUTPUT" | tr -d ' ')
echo "mock output lines: $MOCK_LINES"
test "$MOCK_LINES" -eq 20 && echo "mock output line count OK (20)"

# score with sample predictions
echo ""
echo "--- signaleval score ---"
signaleval score \
  --dataset "$DEMO_DATASET" \
  --predictions "$SAMPLE_PREDS"

# score with json output
SCORE_JSON="$TMPDIR/score.json"
signaleval score \
  --dataset "$DEMO_DATASET" \
  --predictions "$SAMPLE_PREDS" \
  --json-output "$SCORE_JSON"
test -f "$SCORE_JSON" && echo "score JSON output created OK"

# report
echo ""
echo "--- signaleval report ---"
REPORT_PATH="$TMPDIR/test-report.md"
signaleval report \
  --dataset "$DEMO_DATASET" \
  --predictions "$SAMPLE_PREDS" \
  --output "$REPORT_PATH"
test -f "$REPORT_PATH" && echo "report file created OK"
grep -q "SignalEval Report" "$REPORT_PATH" && echo "report contains expected header OK"
grep -q "Not financial advice" "$REPORT_PATH" && echo "report contains disclaimer OK"

# score with imperfect predictions
echo ""
echo "--- signaleval score (imperfect predictions) ---"
signaleval score \
  --dataset "$DEMO_DATASET" \
  --predictions "$PROJECT_DIR/examples/predictions/imperfect_predictions.jsonl"

# board command
echo ""
echo "--- signaleval board ---"
BOARD_OUT="$TMPDIR/board-test"
signaleval board \
  --input "$PROJECT_DIR/examples/runs" \
  --output "$BOARD_OUT"
test -f "$BOARD_OUT/index.html"              && echo "board index.html created OK"
test -f "$BOARD_OUT/assets/style.css"        && echo "board style.css created OK"
test -f "$BOARD_OUT/data/leaderboard.json"   && echo "board leaderboard.json created OK"
grep -q "SignalEvalRunner Board"             "$BOARD_OUT/index.html" && echo "board header OK"
grep -q "Research only"                      "$BOARD_OUT/index.html" && echo "board disclaimer OK"
grep -q "simple-baseline\|oracle-baseline\|local-llm-sample" \
                                             "$BOARD_OUT/index.html" && echo "board models OK"
RANK1=$(python3 -c "import json; d=json.load(open('$BOARD_OUT/data/leaderboard.json')); print(d['rows'][0]['model'])")
echo "board rank-1 model: $RANK1"

echo ""
echo "========================================"
echo "  Smoke test PASSED"
echo "========================================"
