from pathlib import Path
from typing import Dict, Any, List

from .base import BaseProvider
from .. import providers
from ..utils.jsonl import read_jsonl


@providers.register("file")
class FileProvider(BaseProvider):
    name = "file"

    def __init__(self, predictions_file: str = "", **kwargs):
        if not predictions_file:
            raise ValueError("FileProvider requires --predictions-file path")
        path = Path(predictions_file)
        if not path.exists():
            raise FileNotFoundError(f"Predictions file not found: {path}")
        rows = read_jsonl(path)
        self._pred_map: Dict[str, dict] = {r["id"]: r for r in rows if "id" in r}
        print(f"FileProvider loaded {len(self._pred_map)} predictions from {path}")

    def predict(self, row: Dict[str, Any]) -> Dict[str, Any]:
        rid = row["id"]
        pred = self._pred_map.get(rid)
        if pred is None:
            return {
                "id": rid,
                "predicted_direction": "neutral",
                "predicted_event_type": "other",
                "predicted_time_horizon": "short_term",
                "predicted_confidence": "low",
                "reasoning": "No prediction found in file for this id.",
                "provider": "file",
            }
        return pred
