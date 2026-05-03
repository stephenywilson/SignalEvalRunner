import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from .schema import ScoreResult
from .scorer import score, build_confusion
from .utils.jsonl import read_jsonl


def pct(v: float) -> str:
    return f"{v * 100:.1f}%"


def _display_path(p: Path) -> str:
    try:
        return str(p.relative_to(Path.cwd()))
    except ValueError:
        return str(p)


def generate_report(
    dataset_path: Path,
    predictions_path: Path,
    output_path=None,
) -> str:
    dataset_rows = read_jsonl(dataset_path)
    prediction_rows = read_jsonl(predictions_path)

    result, missed = score(dataset_rows, prediction_rows)
    confusion = build_confusion(dataset_rows, prediction_rows)

    lines = []
    lines.append("# SignalEval Report")
    lines.append(f"\n_Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_\n")

    lines.append("## Summary\n")
    lines.append(f"- **Dataset**: `{_display_path(Path(dataset_path))}`")
    lines.append(f"- **Predictions**: `{_display_path(Path(predictions_path))}`")
    lines.append(f"- **Total dataset rows**: {result.total_dataset_rows}")
    lines.append(f"- **Total prediction rows**: {result.total_prediction_rows}")
    lines.append(f"- **Coverage**: {pct(result.coverage)} ({result.matched_rows}/{result.total_dataset_rows} rows matched)")
    lines.append(f"- **Macro score**: {pct(result.macro_score)}")

    lines.append("\n## Metrics\n")
    lines.append(f"| Metric | Score |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Direction accuracy | {pct(result.direction_accuracy)} |")
    lines.append(f"| Event type accuracy | {pct(result.event_type_accuracy)} |")
    lines.append(f"| Time horizon accuracy | {pct(result.time_horizon_accuracy)} |")
    lines.append(f"| Confidence match | {pct(result.confidence_match)} |")
    lines.append(f"| Coverage | {pct(result.coverage)} |")
    lines.append(f"| Macro score | {pct(result.macro_score)} |")
    lines.append(f"| Invalid predictions | {result.invalid_prediction_count} |")

    lines.append("\n## Confusion Summary (Direction)\n")
    directions = ["bullish", "bearish", "neutral", "mixed"]
    header = "| Expected \\\\ Predicted | " + " | ".join(directions) + " |"
    sep = "|---|" + "---|" * len(directions)
    lines.append(header)
    lines.append(sep)
    for expected in directions:
        row_vals = [str(confusion.get(expected, {}).get(p, 0)) for p in directions]
        lines.append(f"| **{expected}** | " + " | ".join(row_vals) + " |")

    if missed:
        lines.append("\n## Missed Examples (Direction Wrong)\n")
        lines.append("_Showing up to 10 examples where direction prediction was incorrect._\n")
        for ex in missed[:10]:
            lines.append(f"**ID**: `{ex['id']}`  ")
            lines.append(f"**Headline**: {ex['headline']}  ")
            lines.append(f"**Expected direction**: `{ex['expected_direction']}` → **Predicted**: `{ex['predicted_direction']}`  ")
            lines.append(f"**Expected event type**: `{ex['expected_event_type']}` → **Predicted**: `{ex['predicted_event_type']}`  ")
            lines.append("")

    lines.append("\n## Notes\n")
    lines.append("> **Research only. Not financial advice. No trading execution.**")
    lines.append("> This report evaluates model output quality on structured prediction tasks only.")
    lines.append("> No investment recommendations are made. Reasoning quality grading is planned for v0.2.")


    report_text = "\n".join(lines) + "\n"

    if output_path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_text, encoding="utf-8")

    return report_text
