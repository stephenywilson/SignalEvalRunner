# Changelog

All notable changes to SignalEval Runner are documented here.

---

## [0.1.1] — 2026-05-03

### Release hardening pass

- **Version**: bumped to `0.1.1` in `pyproject.toml` and `signaleval/__init__.py`
- **CLI**: `signaleval --version` now outputs `SignalEval Runner 0.1.1` (was `signaleval 0.1.0`)
- **CLI**: verified `python -m signaleval --help` works via `__main__.py`
- **Report**: report generator now emits relative paths instead of absolute local paths
- **Sample report**: added `examples/reports/sample-report.md` generated from demo dataset
- **Scripts**: added `scripts/check_release.sh` for pre-release verification
- **Scorer**: fixed `None.strip()` crash when a prediction field is explicitly set to `null`
- **Scorer**: added duplicate prediction id warning (last occurrence wins, stderr warning)
- **Validate**: fixed `validate_predictions` return type annotation (3-tuple)
- **Security**: confirmed no API keys, no private paths in source or generated outputs
- **Docs**: confirmed no private data, no trading claims in any doc

---

## [0.1.0] — 2026-05-03

### Initial MVP release

**CLI commands:**
- `signaleval init` — initialize `.signaleval/` config and output directories
- `signaleval validate` — validate dataset JSONL format and label constraints
- `signaleval run` — run a provider on a dataset and write predictions
- `signaleval score` — score predictions against ground truth dataset
- `signaleval report` — generate Markdown evaluation report
- `signaleval providers` — list providers and their requirements

**Providers:**
- `mock` — deterministic seeded predictions, no API key, safe for CI
- `file` — read predictions from existing JSONL file
- `ollama` — local inference via Ollama (localhost:11434)
- `openai` — OpenAI chat completions via `OPENAI_API_KEY`
- `anthropic` — Anthropic Messages API via `ANTHROPIC_API_KEY`

**Evaluation metrics:**
- Direction accuracy (exact match)
- Event type accuracy (exact match)
- Time horizon accuracy (exact match)
- Confidence match (exact match)
- Coverage (% rows with matching prediction)
- Macro score (mean of 5 metrics)
- Direction confusion matrix

**Data:**
- 20-row synthetic demo dataset (`examples/datasets/demo.jsonl`)
- Sample predictions at ~85% accuracy (`examples/predictions/sample_predictions.jsonl`)
- Imperfect predictions at ~55% accuracy (`examples/predictions/imperfect_predictions.jsonl`)

**Docs:**
- `docs/providers.md` — provider setup and usage
- `docs/output-format.md` — dataset and prediction JSONL format
- `docs/local-models.md` — Ollama local model guide
- `docs/evaluation-metrics.md` — metrics explanation and limitations
- `docs/github-release.md` — GitHub release notes template

**Schema:**
- `schema/news_signal_dataset.schema.json`
- `schema/news_signal_prediction.schema.json`

**Testing:**
- `scripts/smoke_test.sh` — end-to-end smoke test (no external APIs)

---

## Planned for v0.2

- Partial credit scoring for adjacent labels
- Reasoning quality scoring via judge model
- Per-event-type metric breakdown
- Calibration analysis for confidence predictions
- Asset prediction accuracy metric
- CSV output option for score command
- Batch run support (multiple prediction files)
