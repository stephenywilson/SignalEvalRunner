from pathlib import Path
from typing import List, Dict, Tuple, Optional

from .schema import ScoreResult, ALLOWED_DIRECTIONS
from .utils.jsonl import read_jsonl
from .validate import validate_predictions


def _is_blank(value) -> bool:
    return value is None or str(value).strip() == ""


def score(dataset_rows: List[dict], prediction_rows: List[dict]) -> Tuple[ScoreResult, List[dict]]:
    # Build pred_map; warn on duplicate ids (last occurrence wins)
    pred_map: Dict[str, dict] = {}
    seen_ids: set = set()
    for p in prediction_rows:
        if "id" not in p:
            continue
        pid = p["id"]
        if pid in seen_ids:
            import sys
            print(f"Warning: duplicate prediction id '{pid}' — using last occurrence", file=sys.stderr)
        seen_ids.add(pid)
        pred_map[pid] = p

    required = ["id", "predicted_direction", "predicted_event_type",
                "predicted_time_horizon", "predicted_confidence", "reasoning"]
    invalid_count = sum(
        1 for p in prediction_rows if any(_is_blank(p.get(f)) for f in required)
    )

    direction_hits = 0
    event_hits = 0
    horizon_hits = 0
    confidence_hits = 0
    matched = 0
    missed_examples = []

    for row in dataset_rows:
        rid = row["id"]
        pred = pred_map.get(rid)
        if pred is None:
            continue
        matched += 1

        dir_ok = pred.get("predicted_direction") == row["expected_direction"]
        evt_ok = pred.get("predicted_event_type") == row["event_type"]
        hor_ok = pred.get("predicted_time_horizon") == row["time_horizon"]
        con_ok = pred.get("predicted_confidence") == row["confidence_label"]

        if dir_ok:
            direction_hits += 1
        if evt_ok:
            event_hits += 1
        if hor_ok:
            horizon_hits += 1
        if con_ok:
            confidence_hits += 1

        if not dir_ok:
            missed_examples.append({
                "id": rid,
                "headline": row.get("headline", ""),
                "expected_direction": row["expected_direction"],
                "predicted_direction": pred.get("predicted_direction", ""),
                "expected_event_type": row["event_type"],
                "predicted_event_type": pred.get("predicted_event_type", ""),
            })

    n = matched if matched > 0 else 1
    total = len(dataset_rows) if len(dataset_rows) > 0 else 1
    coverage = matched / len(dataset_rows) if dataset_rows else 0.0

    direction_acc = direction_hits / n
    event_acc = event_hits / n
    horizon_acc = horizon_hits / n
    confidence_acc = confidence_hits / n
    macro = (direction_acc + event_acc + horizon_acc + confidence_acc + coverage) / 5.0

    result = ScoreResult(
        direction_accuracy=direction_acc,
        event_type_accuracy=event_acc,
        time_horizon_accuracy=horizon_acc,
        confidence_match=confidence_acc,
        coverage=coverage,
        invalid_prediction_count=invalid_count,
        macro_score=macro,
        total_dataset_rows=len(dataset_rows),
        total_prediction_rows=len(prediction_rows),
        matched_rows=matched,
    )
    return result, missed_examples


def build_confusion(dataset_rows: List[dict], prediction_rows: List[dict]) -> Dict[str, Dict[str, int]]:
    pred_map = {p["id"]: p for p in prediction_rows if "id" in p}
    confusion: Dict[str, Dict[str, int]] = {d: {d2: 0 for d2 in ALLOWED_DIRECTIONS} for d in ALLOWED_DIRECTIONS}

    for row in dataset_rows:
        pred = pred_map.get(row["id"])
        if pred is None:
            continue
        expected = row["expected_direction"]
        predicted = pred.get("predicted_direction", "")
        if expected in confusion and predicted in confusion[expected]:
            confusion[expected][predicted] += 1

    return confusion
