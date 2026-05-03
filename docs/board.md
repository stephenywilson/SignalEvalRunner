# Static Board Export

`signaleval board` generates a self-contained static HTML leaderboard from evaluation result JSON files.

---

## What it does

- Reads run result JSON files from an input directory
- Normalizes them into a ranked leaderboard
- Writes `index.html`, `assets/style.css`, and `data/leaderboard.json` to an output directory
- Works offline, no server required, no external dependencies

---

## Quick start

```bash
# Generate board from example runs
signaleval board --input examples/runs --output site-demo

# Open in browser
open site-demo/index.html          # macOS
xdg-open site-demo/index.html     # Linux
start site-demo/index.html        # Windows
```

---

## Output structure

```
<output-dir>/
  index.html          # Main leaderboard page
  assets/
    style.css         # Dark-theme stylesheet (no external resources)
  data/
    leaderboard.json  # Machine-readable leaderboard data
```

---

## Input directory format

The input directory should contain one or more `.json` files, each representing a single model evaluation run.

### Full format

```json
{
  "model": "gpt-4.1-mini",
  "provider": "openai",
  "dataset": "demo",
  "created_at": "2026-05-03T12:00:00Z",
  "notes": "Research only.",
  "scores": {
    "overall": 0.82,
    "direction_accuracy": 0.78,
    "event_type_accuracy": 0.81,
    "asset_match": 0.76,
    "time_horizon_match": 0.74,
    "reasoning_quality": 0.84
  },
  "counts": {
    "total": 50,
    "passed": 41,
    "failed": 9
  }
}
```

### Simple fallback format

```json
{
  "model": "simple-baseline",
  "overall": 0.65,
  "direction_accuracy": 0.62,
  "event_type_accuracy": 0.70
}
```

### Supported fields

| Field | Required | Description |
|-------|----------|-------------|
| `model` | Recommended | Model name. Falls back to filename stem if missing. |
| `provider` | No | Provider used (openai, anthropic, ollama, file, mock) |
| `dataset` | No | Dataset name |
| `created_at` | No | ISO 8601 timestamp |
| `notes` | No | Free-text notes |
| `scores.overall` | No | Overall score 0.0–1.0 |
| `scores.direction_accuracy` | No | Direction prediction accuracy |
| `scores.event_type_accuracy` | No | Event type accuracy |
| `scores.asset_match` | No | Asset match accuracy |
| `scores.time_horizon_match` | No | Time horizon accuracy |
| `scores.reasoning_quality` | No | Reasoning quality (requires judge model) |
| `counts.total` | No | Total examples evaluated |
| `counts.passed` | No | Passed count |
| `counts.failed` | No | Failed count |

Top-level score fields (e.g. `"overall": 0.82`) are also accepted as a fallback when `scores` is absent.

All fields are optional except that at least one of them should be meaningful. Missing score fields display as `—` in the generated table.

---

## Sorting

Rows are sorted by `overall` score descending. Runs without an `overall` score appear last. Ties are broken alphabetically by model name.

---

## Leaderboard columns

| Column | Source field |
|--------|-------------|
| Rank | Computed |
| Model | `model` |
| Provider | `provider` |
| Dataset | `dataset` |
| Overall | `scores.overall` or `overall` |
| Direction | `scores.direction_accuracy` |
| Event Type | `scores.event_type_accuracy` |
| Asset Match | `scores.asset_match` |
| Time Horizon | `scores.time_horizon_match` |
| Reasoning | `scores.reasoning_quality` |
| Examples | `counts.total` |
| Generated At | `created_at` |

---

## Error handling

| Situation | Behavior |
|-----------|----------|
| Input directory missing | Error, exit non-zero |
| No JSON files in directory | Error, exit non-zero |
| Invalid JSON file | Warning printed, file skipped |
| All files invalid | Error, exit non-zero |
| Output directory missing | Created automatically |
| Output directory exists | Existing files overwritten safely |

---

## Deploying to GitHub Pages

1. Generate the site:
   ```bash
   signaleval board --input examples/runs --output docs/board
   ```
2. Commit the output:
   ```bash
   git add docs/board
   git commit -m "Update leaderboard"
   git push
   ```
3. In your GitHub repository settings, enable GitHub Pages and set the source to the `docs/` folder.

The generated site has no server requirements — it runs from the file system or any static host.

---

## Limitations

- Scores are taken as-is from JSON files. SignalEval Runner does not verify that scores came from a real evaluation run.
- `reasoning_quality` requires a judge model or human labels to produce meaningful scores. It displays as `—` if not present.
- The board is static: adding a new run requires regenerating the site.
- No authentication, no user accounts, no live data.
- Research only. Not financial advice. No trading execution.
```
