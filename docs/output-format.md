# Output Format

## Dataset JSONL format

Each line is a JSON object representing one news item with a ground-truth signal label.

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique row identifier |
| `headline` | string | News headline |
| `body` | string | News body text |
| `asset` | string | Asset ticker or name (e.g. `SPY`, `BTC`) |
| `asset_type` | string | Asset class (e.g. `stock`, `etf`, `crypto`, `commodity`) |
| `event_type` | string | Event category (see allowed values below) |
| `expected_direction` | string | Ground truth: `bullish`, `bearish`, `neutral`, `mixed` |
| `time_horizon` | string | `intraday`, `short_term`, `medium_term`, `long_term` |
| `confidence_label` | string | `low`, `medium`, `high` |
| `rationale` | string | Human explanation for the label |

### Example row

```json
{
  "id": "demo_001",
  "headline": "Federal Reserve holds rates steady, signals two cuts in 2025",
  "body": "The Federal Open Market Committee voted unanimously ...",
  "asset": "SPY",
  "asset_type": "etf",
  "event_type": "central_bank",
  "expected_direction": "bullish",
  "time_horizon": "short_term",
  "confidence_label": "high",
  "rationale": "Dovish Fed pivot signal reduces discount rate pressure on equities."
}
```

---

## Prediction JSONL format

Each line is a JSON object representing one model prediction.

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Must match a dataset row id |
| `predicted_direction` | string | `bullish`, `bearish`, `neutral`, `mixed` |
| `predicted_event_type` | string | Event type prediction |
| `predicted_time_horizon` | string | Time horizon prediction |
| `predicted_confidence` | string | `low`, `medium`, `high` |
| `reasoning` | string | Model's one-sentence explanation |

### Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `predicted_asset` | string | Model's asset prediction |
| `model` | string | Model name |
| `provider` | string | Provider used |
| `raw_output` | string | Raw model output before JSON parsing |

### Example row

```json
{
  "id": "demo_001",
  "predicted_direction": "bullish",
  "predicted_event_type": "central_bank",
  "predicted_time_horizon": "short_term",
  "predicted_confidence": "high",
  "reasoning": "Dovish tone and rate cut signal reduces rate risk for equities.",
  "model": "gpt-4o-mini",
  "provider": "openai"
}
```

---

## Scoring alignment

Predictions are matched to dataset rows by `id`. Rows with no matching prediction are counted as missed (reducing coverage score). Extra predictions with no matching dataset row are ignored.
