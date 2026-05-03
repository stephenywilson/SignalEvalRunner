import json
import os
import urllib.request
import urllib.error
from typing import Dict, Any

from .base import BaseProvider
from .. import providers
from ..utils.text import extract_json_from_text


_SYSTEM_PROMPT = """\
You are a financial news analysis assistant. Given a news headline and body, output ONLY a JSON object.
Required fields:
- predicted_direction: one of bullish, bearish, neutral, mixed
- predicted_event_type: one of central_bank, earnings, guidance, inflation, jobs, geopolitics, regulation, merger, product_launch, supply_chain, credit, commodity, crypto, other
- predicted_time_horizon: one of intraday, short_term, medium_term, long_term
- predicted_confidence: one of low, medium, high
- reasoning: one-sentence explanation

Output JSON only. This is research only, not financial advice."""


@providers.register("anthropic")
class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(self, model: str = "claude-haiku-4-5-20251001", **kwargs):
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "ANTHROPIC_API_KEY environment variable is not set.\n"
                "Export it with: export ANTHROPIC_API_KEY=your_key_here\n"
                "Do not store API keys in code or config files."
            )
        self._api_key = api_key
        self._model = model

    def predict(self, row: Dict[str, Any]) -> Dict[str, Any]:
        rid = row.get("id", "unknown")
        user_content = (
            f"Headline: {row.get('headline', '')}\n"
            f"Body: {row.get('body', '')[:800]}\n"
            f"Asset: {row.get('asset', '')} ({row.get('asset_type', '')})"
        )

        payload = json.dumps({
            "model": self._model,
            "max_tokens": 400,
            "system": _SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_content}],
        }).encode()

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "x-api-key": self._api_key,
                "anthropic-version": "2023-06-01",
                "User-Agent": "SignalEvalRunner/0.1",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                raw = result["content"][0]["text"]
        except urllib.error.HTTPError as ex:
            body = ex.read().decode()
            raise RuntimeError(f"Anthropic API error {ex.code}: {body[:200]}")
        except urllib.error.URLError as ex:
            raise ConnectionError(f"Anthropic request failed: {ex}")

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
                "provider": "anthropic",
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
            "provider": "anthropic",
            "model": self._model,
        }
