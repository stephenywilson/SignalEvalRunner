from dataclasses import dataclass
from typing import Optional

from .parser import RunEntry


@dataclass
class BoardRow:
    rank: int
    model: str
    provider: str
    dataset: str
    overall: Optional[float]
    direction_accuracy: Optional[float]
    event_type_accuracy: Optional[float]
    asset_match: Optional[float]
    time_horizon_match: Optional[float]
    reasoning_quality: Optional[float]
    total: Optional[int]
    created_at: str
    source_file: str


def build_leaderboard(entries: list[RunEntry]) -> list[BoardRow]:
    """Sort entries by overall score descending (None last, then model asc) and assign ranks."""

    def sort_key(e: RunEntry):
        # (None-last flag, negated score for descending, model name for ties)
        return (1 if e.overall is None else 0, -(e.overall or 0.0), e.model.lower())

    sorted_entries = sorted(entries, key=sort_key)

    rows = []
    for i, e in enumerate(sorted_entries, start=1):
        rows.append(BoardRow(
            rank=i,
            model=e.model,
            provider=e.provider or "—",
            dataset=e.dataset or "—",
            overall=e.overall,
            direction_accuracy=e.direction_accuracy,
            event_type_accuracy=e.event_type_accuracy,
            asset_match=e.asset_match,
            time_horizon_match=e.time_horizon_match,
            reasoning_quality=e.reasoning_quality,
            total=e.total,
            created_at=e.created_at or "—",
            source_file=e.source_file,
        ))

    return rows
