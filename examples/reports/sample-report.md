# SignalEval Report

_Generated: 2026-05-03 12:26 UTC_

## Summary

- **Dataset**: `examples/datasets/demo.jsonl`
- **Predictions**: `examples/predictions/sample_predictions.jsonl`
- **Total dataset rows**: 20
- **Total prediction rows**: 20
- **Coverage**: 100.0% (20/20 rows matched)
- **Macro score**: 98.0%

## Metrics

| Metric | Score |
|--------|-------|
| Direction accuracy | 90.0% |
| Event type accuracy | 100.0% |
| Time horizon accuracy | 100.0% |
| Confidence match | 100.0% |
| Coverage | 100.0% |
| Macro score | 98.0% |
| Invalid predictions | 0 |

## Confusion Summary (Direction)

| Expected \\ Predicted | bullish | bearish | neutral | mixed |
|---|---|---|---|---|
| **bullish** | 8 | 0 | 0 | 0 |
| **bearish** | 0 | 6 | 1 | 0 |
| **neutral** | 1 | 0 | 2 | 0 |
| **mixed** | 0 | 0 | 0 | 2 |

## Missed Examples (Direction Wrong)

_Showing up to 10 examples where direction prediction was incorrect._

**ID**: `demo_005`  
**Headline**: Nonfarm payrolls add 285,000 jobs in November, unemployment holds at 3.8%  
**Expected direction**: `neutral` → **Predicted**: `bullish`  
**Expected event type**: `jobs` → **Predicted**: `jobs`  

**ID**: `demo_011`  
**Headline**: Central bank of major EM economy raises rates 75bps to combat currency depreciation  
**Expected direction**: `bearish` → **Predicted**: `neutral`  
**Expected event type**: `central_bank` → **Predicted**: `central_bank`  


## Notes

> **Research only. Not financial advice. No trading execution.**
> This report evaluates model output quality on structured prediction tasks only.
> No investment recommendations are made. Reasoning quality grading is planned for v0.2.
