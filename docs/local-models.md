# Local Models with Ollama

SignalEval Runner supports local model inference via [Ollama](https://ollama.ai), which lets you run open-source models entirely on your machine with no API key required.

---

## Setup

1. Install Ollama from https://ollama.ai
2. Start the Ollama server:
   ```bash
   ollama serve
   ```
3. Pull a model:
   ```bash
   ollama pull llama3
   # or
   ollama pull mistral
   # or any model from https://ollama.ai/library
   ```

---

## Usage

```bash
signaleval run \
  --dataset examples/datasets/demo.jsonl \
  --provider ollama \
  --model llama3 \
  --output .signaleval/outputs/llama3_predictions.jsonl
```

---

## How it works

SignalEval sends a prompt to `http://localhost:11434/api/generate` with the model name and a structured news-to-signal instruction.

The prompt instructs the model to output JSON with `predicted_direction`, `predicted_event_type`, `predicted_time_horizon`, `predicted_confidence`, and `reasoning`.

The runner attempts to parse JSON from the model's response using:
1. Direct JSON parse
2. JSON extraction from markdown code block
3. First `{...}` block in the output

If parsing fails, a fallback response with `neutral` direction and `low` confidence is recorded, and `raw_output` is preserved for debugging.

---

## Recommended models

| Model | Size | Notes |
|-------|------|-------|
| `llama3` | 8B | Strong instruction following |
| `mistral` | 7B | Good JSON output compliance |
| `qwen2.5` | 7B | Strong on structured tasks |
| `phi3` | 3.8B | Lightweight option |

---

## Connection error handling

If Ollama is not running when you call the `ollama` provider, SignalEval Runner will print a helpful error:

```
Error: Cannot connect to Ollama at localhost:11434. 
Is Ollama running? Start it with: ollama serve
```

No stack trace is shown for this expected error condition.

---

## Privacy

Local models via Ollama run entirely on your machine. No data is sent to any external API.
