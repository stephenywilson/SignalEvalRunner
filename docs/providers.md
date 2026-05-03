# Providers

SignalEval Runner supports five providers in v0.1.

---

## file

**Purpose:** Read predictions from an existing JSONL file.

Use this when you have already generated model outputs elsewhere and want to score them.

**Required:** `--predictions-file path/to/predictions.jsonl`

**API key required:** No

**Example:**
```bash
signaleval run \
  --dataset examples/datasets/demo.jsonl \
  --provider file \
  --predictions-file examples/predictions/sample_predictions.jsonl \
  --output .signaleval/outputs/file_run.jsonl
```

---

## mock

**Purpose:** Deterministic fake predictions for testing and CI.

The mock provider uses a seeded hash function to produce consistent, reproducible predictions. It never calls any external API.

**API key required:** No

**Example:**
```bash
signaleval run \
  --dataset examples/datasets/demo.jsonl \
  --provider mock \
  --output .signaleval/outputs/mock_run.jsonl
```

---

## ollama

**Purpose:** Run a local model via Ollama.

Ollama must be installed and running locally. The provider calls `http://localhost:11434/api/generate`.

**API key required:** No (local only)

**Requires:** Ollama running (`ollama serve`)

**Install Ollama:** https://ollama.ai

**Example:**
```bash
ollama pull llama3
signaleval run \
  --dataset examples/datasets/demo.jsonl \
  --provider ollama \
  --model llama3 \
  --output .signaleval/outputs/ollama_run.jsonl
```

If Ollama is not running, the runner fails gracefully with a connection error message.

---

## openai

**Purpose:** Call OpenAI's chat completions API.

**API key required:** Yes — set `OPENAI_API_KEY` environment variable.

**Default model:** `gpt-4o-mini`

**Example:**
```bash
export OPENAI_API_KEY=your_key_here
signaleval run \
  --dataset examples/datasets/demo.jsonl \
  --provider openai \
  --model gpt-4o-mini \
  --output .signaleval/outputs/openai_run.jsonl
```

**Security:** The API key is read from the environment variable only. It is never stored, logged, or printed.

---

## anthropic

**Purpose:** Call Anthropic's Messages API.

**API key required:** Yes — set `ANTHROPIC_API_KEY` environment variable.

**Default model:** `claude-haiku-4-5-20251001`

**Example:**
```bash
export ANTHROPIC_API_KEY=your_key_here
signaleval run \
  --dataset examples/datasets/demo.jsonl \
  --provider anthropic \
  --model claude-haiku-4-5-20251001 \
  --output .signaleval/outputs/anthropic_run.jsonl
```

**Security:** The API key is read from the environment variable only. It is never stored, logged, or printed.
