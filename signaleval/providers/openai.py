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


@providers.register("openai")
class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, model: str = "gpt-4o-mini", **kwargs):
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY environment variable is not set.\n"
                "Export it with: export OPENAI_API_KEY=your_key_here\n"
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
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.1,
            "max_tokens": 400,
        }).encode()

        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
                "User-Agent": "SignalEvalRunner/0.1",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode())
                raw = result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as ex:
            body = ex.read().decode()
            raise RuntimeError(f"OpenAI API error {ex.code}: {body[:200]}")
        except urllib.error.URLError as ex:
            raise ConnectionError(f"OpenAI request failed: {ex}")

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
                "provider": "openai",
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
            "provider": "openai",
            "model": self._model,
        }
