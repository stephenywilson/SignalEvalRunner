# GitHub Release Notes

## Repository description

Provider-agnostic CLI runner for financial news-to-signal model evaluation.

## Topics

```
llm-evaluation
financial-news
benchmark
ai-evaluation
model-eval
finance
cli
python
ollama
openai
anthropic
catalayer
```

## v0.1.0 Release Notes

### SignalEval Runner v0.1.0

**Provider-agnostic CLI for evaluating language models on financial news-to-signal tasks.**

This is the initial v0.1 release of SignalEval Runner by Catalayer AI.

#### What is SignalEval Runner?

SignalEval Runner is a lightweight CLI that evaluates whether language models can convert market-moving news into structured signal predictions: direction, event type, time horizon, confidence, and reasoning.

It is designed to work with News2SignalBench-style datasets and can evaluate predictions from local files, mock runs, local models via Ollama, and optional cloud provider integrations (OpenAI, Anthropic).

#### What's included in v0.1.0

- `signaleval init` — initialize config and output folders
- `signaleval validate` — validate dataset JSONL format
- `signaleval run` — run a provider and generate predictions
- `signaleval score` — score predictions against ground truth
- `signaleval report` — generate Markdown evaluation report
- `signaleval providers` — list supported providers

**Providers:**
- `mock` — deterministic fake predictions (no API key, ideal for CI/testing)
- `file` — read predictions from an existing JSONL file
- `ollama` — local inference via Ollama
- `openai` — OpenAI chat completions (requires OPENAI_API_KEY)
- `anthropic` — Anthropic Messages API (requires ANTHROPIC_API_KEY)

**Evaluation metrics:**
- Direction accuracy (primary metric)
- Event type accuracy
- Time horizon accuracy
- Confidence match
- Coverage
- Macro score
- Confusion matrix for direction labels

#### Relationship to News2SignalBench

SignalEval Runner is the evaluation runner. News2SignalBench defines the benchmark dataset format and labeling standard. The two projects are designed to work together but are independently usable.

#### Important

> Research only. Not financial advice. No trading execution.

#### Installation

```bash
pip install signalevalrunner
```

or from source:

```bash
git clone https://github.com/stephenywilson/SignalEvalRunner
cd SignalEvalRunner
pip install -e .
```

#### Quick start

```bash
signaleval validate --dataset examples/datasets/demo.jsonl
signaleval score \
  --dataset examples/datasets/demo.jsonl \
  --predictions examples/predictions/sample_predictions.jsonl
```
