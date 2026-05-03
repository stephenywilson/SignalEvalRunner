import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RunEntry:
    model: str
    provider: Optional[str]
    dataset: Optional[str]
    created_at: Optional[str]
    overall: Optional[float]
    direction_accuracy: Optional[float]
    event_type_accuracy: Optional[float]
    asset_match: Optional[float]
    time_horizon_match: Optional[float]
    reasoning_quality: Optional[float]
    total: Optional[int]
    notes: Optional[str]
    source_file: str


def _f(v) -> Optional[float]:
    if v is None:
        return None
    try:
        return round(float(v), 4)
    except (TypeError, ValueError):
        return None


def _i(v) -> Optional[int]:
    if v is None:
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _pick(primary, fallback):
    """Return primary if not None/falsy, else fallback."""
    return primary if primary is not None else fallback


def parse_run_file(path: Path) -> RunEntry:
    """Parse one run JSON file into RunEntry. Tolerant of missing or extra fields."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("top-level JSON value must be an object")

    scores = data.get("scores") or {}
    counts = data.get("counts") or {}

    return RunEntry(
        model=str(data.get("model") or Path(path).stem),
        provider=data.get("provider") or None,
        dataset=data.get("dataset") or None,
        created_at=data.get("created_at") or None,
        overall=_f(_pick(scores.get("overall"), data.get("overall"))),
        direction_accuracy=_f(_pick(scores.get("direction_accuracy"), data.get("direction_accuracy"))),
        event_type_accuracy=_f(_pick(scores.get("event_type_accuracy"), data.get("event_type_accuracy"))),
        asset_match=_f(_pick(scores.get("asset_match"), data.get("asset_match"))),
        time_horizon_match=_f(_pick(scores.get("time_horizon_match"), data.get("time_horizon_match"))),
        reasoning_quality=_f(_pick(scores.get("reasoning_quality"), data.get("reasoning_quality"))),
        total=_i(_pick(counts.get("total"), data.get("total"))),
        notes=data.get("notes") or None,
        source_file=Path(path).name,
    )


def load_runs_from_dir(directory: Path) -> tuple[list[RunEntry], list[str]]:
    """Load all *.json files from directory.

    Returns (valid_entries, warning_messages).
    Raises FileNotFoundError if directory is missing.
    Raises ValueError if no JSON files exist or none are valid.
    """
    directory = Path(directory)
    if not directory.exists():
        raise FileNotFoundError(f"Input directory not found: {directory}")

    json_files = sorted(directory.glob("*.json"))
    if not json_files:
        raise ValueError(f"No JSON files found in: {directory}")

    entries: list[RunEntry] = []
    warnings: list[str] = []

    for f in json_files:
        try:
            entries.append(parse_run_file(f))
        except Exception as ex:
            warnings.append(f"Skipping {f.name}: {ex}")

    if not entries:
        raise ValueError(f"No valid run files could be parsed in: {directory}")

    return entries, warnings
