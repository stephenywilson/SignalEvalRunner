import json
import sys
from pathlib import Path
from typing import List, Tuple

from .schema import (
    DATASET_REQUIRED_FIELDS, PREDICTION_REQUIRED_FIELDS,
    ALLOWED_DIRECTIONS, ALLOWED_TIME_HORIZONS,
    ALLOWED_CONFIDENCE_LABELS, ALLOWED_EVENT_TYPES
)
from .utils.jsonl import read_jsonl


def validate_dataset(path: Path) -> Tuple[List[dict], List[str]]:
    rows = read_jsonl(path)
    errors = []
    for i, row in enumerate(rows):
        row_id = row.get("id", f"row_{i}")
        for field in DATASET_REQUIRED_FIELDS:
            if field not in row or row[field] is None or str(row[field]).strip() == "":
                errors.append(f"Row {row_id}: missing required field '{field}'")
        if "expected_direction" in row and row["expected_direction"] not in ALLOWED_DIRECTIONS:
            errors.append(f"Row {row_id}: invalid expected_direction '{row['expected_direction']}' (allowed: {sorted(ALLOWED_DIRECTIONS)})")
        if "time_horizon" in row and row["time_horizon"] not in ALLOWED_TIME_HORIZONS:
            errors.append(f"Row {row_id}: invalid time_horizon '{row['time_horizon']}' (allowed: {sorted(ALLOWED_TIME_HORIZONS)})")
        if "confidence_label" in row and row["confidence_label"] not in ALLOWED_CONFIDENCE_LABELS:
            errors.append(f"Row {row_id}: invalid confidence_label '{row['confidence_label']}' (allowed: {sorted(ALLOWED_CONFIDENCE_LABELS)})")
        if "event_type" in row and row["event_type"] not in ALLOWED_EVENT_TYPES:
            errors.append(f"Row {row_id}: invalid event_type '{row['event_type']}' (allowed: {sorted(ALLOWED_EVENT_TYPES)})")
    return rows, errors


def validate_predictions(path: Path) -> Tuple[List[dict], List[str], int]:
    rows = read_jsonl(path)
    errors = []
    invalid_count = 0
    for i, row in enumerate(rows):
        row_id = row.get("id", f"row_{i}")
        row_invalid = False
        for field in PREDICTION_REQUIRED_FIELDS:
            if field not in row or row[field] is None or str(row[field]).strip() == "":
                errors.append(f"Row {row_id}: missing required field '{field}'")
                row_invalid = True
        if "predicted_direction" in row and row["predicted_direction"] not in ALLOWED_DIRECTIONS:
            errors.append(f"Row {row_id}: invalid predicted_direction '{row['predicted_direction']}'")
            row_invalid = True
        if "predicted_time_horizon" in row and row["predicted_time_horizon"] not in ALLOWED_TIME_HORIZONS:
            errors.append(f"Row {row_id}: invalid predicted_time_horizon '{row['predicted_time_horizon']}'")
            row_invalid = True
        if "predicted_confidence" in row and row["predicted_confidence"] not in ALLOWED_CONFIDENCE_LABELS:
            errors.append(f"Row {row_id}: invalid predicted_confidence '{row['predicted_confidence']}'")
            row_invalid = True
        if row_invalid:
            invalid_count += 1
    return rows, errors, invalid_count


def print_validation_summary(path: Path, rows: List[dict], errors: List[str], label: str = "dataset"):
    print(f"\n{label}: {path}")
    print(f"  Total rows: {len(rows)}")
    if errors:
        print(f"  Errors found: {len(errors)}")
        for e in errors[:10]:
            print(f"    - {e}")
        if len(errors) > 10:
            print(f"    ... and {len(errors) - 10} more")
    else:
        print(f"  All rows valid.")
