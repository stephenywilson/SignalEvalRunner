# Contributing to SignalEval Runner

Thank you for your interest in contributing to SignalEval Runner.

---

## Development setup

```bash
git clone https://github.com/stephenywilson/SignalEvalRunner
cd SignalEvalRunner
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

---

## Running the smoke test

The smoke test covers all core CLI commands using only the mock and file providers (no external API calls required):

```bash
bash scripts/smoke_test.sh
```

This should pass on any machine with Python 3.10+.

---

## Project structure

```
signaleval/          Python package
  cli.py             Argument parsing and command dispatch
  config.py          Config init and load
  runner.py          Provider execution loop
  scorer.py          Scoring and confusion matrix
  report.py          Markdown report generation
  schema.py          Data classes and allowed label sets
  validate.py        Dataset and prediction validation
  providers/         Provider implementations
  utils/             JSONL, text, path helpers
  prompts/           Prompt templates
examples/            Demo dataset and example predictions
schema/              JSON Schema definitions
docs/                Documentation
scripts/             Shell utilities
```

---

## Adding a new provider

1. Create `signaleval/providers/your_provider.py`
2. Inherit from `BaseProvider` (in `providers/base.py`)
3. Decorate the class with `@providers.register("your_provider_name")`
4. Implement the `predict(self, row: dict) -> dict` method
5. Import it at the bottom of `signaleval/providers/__init__.py`
6. Document it in `docs/providers.md`

---

## Code guidelines

- Python 3.10+ only
- No runtime dependencies (standard library only unless strongly justified)
- No API calls in smoke test
- No API keys in code or config
- Clear terminal output and helpful error messages
- No stack traces for expected user errors

---

## Contribution guidelines

- Open an issue before large changes
- Keep PRs focused
- Include smoke test evidence that your change works
- Do not add external runtime dependencies without discussion
- Do not include private data, private keys, or internal business logic

---

## License

Contributions are licensed under Apache-2.0, matching the project license.
