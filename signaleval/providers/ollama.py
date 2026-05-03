import json
import urllib.request
import urllib.error
from typing import Dict, Any

from .base import BaseProvider
from .. import providers
from ..utils.text import extract_json_from_text


OLLAMA_DEFAULT_URL = "http://localhost:11434/api/generate"

_SYSTEM_PROMPT = """\
You are a financial news analysis assistant. Given a news item, output ONLY a JSON object with these fields:
- predicted_direction: one of bullish, bearish, neutral, mixed
- predicted_event_type: one of central_bank, earnings, guidance, inflation, jobs, geopolitics, regulation, merger, product_launch, supply_chain, credit, commodity, crypto, other
- predicted_time_horizon: one of intraday, short_term, medium_term, long_term
- predicted_confidence: one of low, medium, high
- reasoning: a one-sentence explanation

Output JSON only. No markdown, no commentary. Not financial advice."""


@providers.register("ollama")
class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self, model: str = "llama3", ollama_url: str = OLLAMA_DEFAULT_URL, **kwargs):
        self._model = model
        self._url = ollama_url
        self._check_connection()

    def _check_connection(self):
        try:
            req = urllib.request.Request(
                "http://localhost:11434/api/tags",
                method="GET",
                headers={"User-Agent": "SignalEvalRunner/0.1"},
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                resp.read()
        except Exception as ex:
            raise ConnectionError(
                f"Cannot connect to Ollama at localhost:11434. "
                f"Is Ollama running? Start it with: ollama serve\n"
                f"Error: {ex}"
            )

    def predict(self, row: Dict[str, Any]) -> Dict[str, Any]:
        rid = row.get("id", "unknown")
        prompt = (
            f"{_SYSTEM_PROMPT}\n\n"
            f"Headline: {row.get('headline', '')}\n"
            f"Body: {row.get('body', '')[:500]}\n"
            f"Asset: {row.get('asset', '')} ({row.get('asset_type', '')})\n\n"
            f"Output JSON only:"
        )

        payload = json.dumps({"model": self._model, "prompt": prompt, "stream": False}).encode()
        req = urllib.request.Request(
            self._url,
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json", "User-Agent": "SignalEvalRunner/0.1"},
        )

        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode())
                raw = result.get("response", "")
        except urllib.error.URLError as ex:
            raise ConnectionError(f"Ollama request failed: {ex}")

        parsed = extract_json_from_text(raw)
        if parsed is None:
            return {
                "id": rid,
                "predicted_direction": "neutral",
                "predicted_event_type": "other",
                "predicted_time_horizon": "short_term",
                "predicted_confidence": "low",
                "reasoning": "Could not parse model output.",
                "raw_output": raw[:500],
                "provider": "ollama",
                "model": self._model,
            }

        return {
            "id": rid,
            "predicted_direction": parsed.get("predicted_direction", "neutral"),
            "predicted_event_type": parsed.get("predicted_event_type", "other"),
            "predicted_time_horizon": parsed.get("predicted_time_horizon", "short_term"),
            "predicted_confidence": parsed.get("predicted_confidence", "low"),
            "reasoning": parsed.get("reasoning", ""),
            "raw_output": raw[:500],
            "provider": "ollama",
            "model": self._model,
        }
