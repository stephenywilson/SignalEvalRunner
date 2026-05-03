# Evaluation Metrics

SignalEval Runner v0.1 uses simple, transparent metrics designed to be reproducible without requiring a judge model.

---

## Metrics

### Direction Accuracy

Exact match between `expected_direction` and `predicted_direction`.

Allowed values: `bullish`, `bearish`, `neutral`, `mixed`

This is the primary metric. Getting direction right is the core capability being tested.

### Event Type Accuracy

Exact match between `event_type` and `predicted_event_type`.

Tests whether the model can correctly categorize the type of market-moving event.

### Time Horizon Accuracy

Exact match between `time_horizon` and `predicted_time_horizon`.

Tests whether the model correctly identifies the timeframe over which the signal applies.

### Confidence Match

Exact match between `confidence_label` and `predicted_confidence`.

Note: This is the noisiest metric. Confidence calibration is inherently subjective and exact-match scoring understates partial agreement.

### Coverage

Percentage of dataset rows that have a matching prediction by `id`.

```
coverage = matched_rows / total_dataset_rows
```

A model that skips rows still loses points. Missing predictions are not counted as correct.

### Invalid Prediction Count

Number of predictions with missing required fields or unsupported label values. Invalid predictions are excluded from accuracy calculations but reduce the overall quality signal.

### Macro Score

Simple arithmetic mean of five metrics:

```
macro_score = (direction_accuracy + event_type_accuracy + time_horizon_accuracy + confidence_match + coverage) / 5
```

---

## Limitations

### v0.1 limitations

- **Exact match only.** `bullish` vs `mixed` is penalized the same as `bullish` vs `bearish`, even though these are qualitatively different errors.
- **No reasoning quality scoring.** Reasoning is stored but not graded. Evaluating reasoning quality reliably requires either human annotation or a judge model — both are out of scope for v0.1.
- **Confidence calibration not measured.** The confidence match metric only checks exact label match, not whether confidence scores are well-calibrated across the dataset.
- **No asset prediction scoring.** `predicted_asset` is accepted but not scored in v0.1.

### Planned for v0.2

- Partial credit for adjacent labels (e.g. `bullish` vs `mixed` scored as 0.5)
- Reasoning quality scoring via judge model
- Calibration analysis for confidence predictions
- Per-event-type breakdown
- Asset prediction accuracy

---

## Research only

These metrics measure model output quality on structured prediction tasks. They do not measure real-world trading performance, financial return, or investment suitability. This tool is for research and evaluation purposes only.
