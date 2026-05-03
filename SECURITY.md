# Security Policy

## API key handling

SignalEval Runner never stores, logs, or prints API keys.

- API keys are read exclusively from environment variables (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`)
- Keys are never written to config files, output files, or log output
- If a key is missing, the CLI prints a clear error without revealing any partial key value
- The config file at `.signaleval/config.json` contains no secrets

## External API calls

External API calls (OpenAI, Anthropic) are made only when:
1. The user explicitly selects the `openai` or `anthropic` provider via `--provider`
2. The corresponding environment variable is set

The `mock` and `file` providers make no external network calls. The `ollama` provider calls only `localhost:11434`.

## Data privacy

- The smoke test (`scripts/smoke_test.sh`) uses only synthetic demo data and makes no external API calls
- User-provided dataset content is sent to external providers only when the user explicitly selects an external provider
- No telemetry, no analytics, no data collection of any kind

## Private data

Do not submit pull requests containing:
- Real API keys or secrets of any kind
- Private or paywalled financial data
- Internal business logic or private model outputs

## Responsible disclosure

If you discover a security issue in SignalEval Runner, please report it by opening a GitHub issue marked `[SECURITY]` or contact the maintainers directly.

This is an open-source research tool. There is no production deployment or user data to protect beyond local usage.
