import hashlib
from typing import Dict, Any

from .base import BaseProvider
from .. import providers
from ..schema import ALLOWED_DIRECTIONS, ALLOWED_TIME_HORIZONS, ALLOWED_CONFIDENCE_LABELS, ALLOWED_EVENT_TYPES


_DIRECTIONS = sorted(ALLOWED_DIRECTIONS)
_HORIZONS = sorted(ALLOWED_TIME_HORIZONS)
_CONFIDENCES = sorted(ALLOWED_CONFIDENCE_LABELS)
_EVENT_TYPES = sorted(ALLOWED_EVENT_TYPES)

_MOCK_REASONINGS = [
    "The headline suggests positive market sentiment driven by the reported event.",
    "Macro indicators and the event context point to downward pressure on the asset.",
    "The news appears broadly neutral with limited direct market-moving implications.",
    "Conflicting signals in the report make the directional outcome uncertain.",
    "Strong forward guidance and beat expectations indicate upside momentum.",
    "Regulatory headwinds and uncertainty suggest a cautious market response.",
    "The central bank statement implies tightening conditions ahead.",
    "Supply disruption signals potential short-term upward price pressure.",
]


def _pick(items, seed_str):
    digest = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
    return items[digest % len(items)]


@providers.register("mock")
class MockProvider(BaseProvider):
    name = "mock"

    def __init__(self, seed: str = "signaleval", **kwargs):
        self._seed = seed

    def predict(self, row: Dict[str, Any]) -> Dict[str, Any]:
        rid = row.get("id", "unknown")
        base = f"{self._seed}:{rid}"

        direction = _pick(_DIRECTIONS, base + ":dir")
        event_type = _pick(_EVENT_TYPES, base + ":evt")
        horizon = _pick(_HORIZONS, base + ":hor")
        confidence = _pick(_CONFIDENCES, base + ":con")
        reasoning = _pick(_MOCK_REASONINGS, base + ":rsn")

        return {
            "id": rid,
            "predicted_direction": direction,
            "predicted_event_type": event_type,
            "predicted_time_horizon": horizon,
            "predicted_confidence": confidence,
            "reasoning": reasoning,
            "model": "mock-v0.1",
            "provider": "mock",
        }
