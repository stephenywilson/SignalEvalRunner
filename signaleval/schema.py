from dataclasses import dataclass, field
from typing import Optional

ALLOWED_DIRECTIONS = {"bullish", "bearish", "neutral", "mixed"}
ALLOWED_TIME_HORIZONS = {"intraday", "short_term", "medium_term", "long_term"}
ALLOWED_CONFIDENCE_LABELS = {"low", "medium", "high"}
ALLOWED_EVENT_TYPES = {
    "central_bank", "earnings", "guidance", "inflation", "jobs",
    "geopolitics", "regulation", "merger", "product_launch",
    "supply_chain", "credit", "commodity", "crypto", "other"
}

DATASET_REQUIRED_FIELDS = [
    "id", "headline", "body", "asset", "asset_type", "event_type",
    "expected_direction", "time_horizon", "confidence_label", "rationale"
]

PREDICTION_REQUIRED_FIELDS = [
    "id", "predicted_direction", "predicted_event_type",
    "predicted_time_horizon", "predicted_confidence", "reasoning"
]


@dataclass
class DatasetRow:
    id: str
    headline: str
    body: str
    asset: str
    asset_type: str
    event_type: str
    expected_direction: str
    time_horizon: str
    confidence_label: str
    rationale: str


@dataclass
class PredictionRow:
    id: str
    predicted_direction: str
    predicted_event_type: str
    predicted_time_horizon: str
    predicted_confidence: str
    reasoning: str
    predicted_asset: Optional[str] = None
    model: Optional[str] = None
    provider: Optional[str] = None
    raw_output: Optional[str] = None


@dataclass
class ScoreResult:
    direction_accuracy: float
    event_type_accuracy: float
    time_horizon_accuracy: float
    confidence_match: float
    coverage: float
    invalid_prediction_count: int
    macro_score: float
    total_dataset_rows: int
    total_prediction_rows: int
    matched_rows: int
