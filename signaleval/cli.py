import argparse
import json
import sys
from pathlib import Path

from . import __version__


def cmd_init(args):
    from .config import init_config
    init_config(force=getattr(args, "force", False))


def cmd_validate(args):
    from .validate import validate_dataset, print_validation_summary
    from .utils.jsonl import read_jsonl

    path = Path(args.dataset)
    try:
        rows, errors = validate_dataset(path)
    except FileNotFoundError as ex:
        print(f"Error: {ex}", file=sys.stderr)
        sys.exit(1)
    except ValueError as ex:
        print(f"Error reading dataset: {ex}", file=sys.stderr)
        sys.exit(1)

    print_validation_summary(path, rows, errors, label="Dataset")

    if errors:
        sys.exit(1)


def cmd_run(args):
    from .runner import run_provider

    dataset_path = Path(args.dataset)
    output_path = Path(args.output)
    provider_name = args.provider

    provider_kwargs = {}
    if hasattr(args, "predictions_file") and args.predictions_file:
        provider_kwargs["predictions_file"] = args.predictions_file
    if hasattr(args, "model") and args.model:
        provider_kwargs["model"] = args.model

    try:
        run_provider(dataset_path, provider_name, output_path, **provider_kwargs)
    except (ValueError, FileNotFoundError, ConnectionError, EnvironmentError) as ex:
        print(f"Error: {ex}", file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        raise
    except Exception as ex:
        print(f"Unexpected error: {ex}", file=sys.stderr)
        sys.exit(1)


def cmd_score(args):
    from .scorer import score
    from .utils.jsonl import read_jsonl
    from .validate import validate_dataset, validate_predictions

    dataset_path = Path(args.dataset)
    predictions_path = Path(args.predictions)

    try:
        dataset_rows, d_errors = validate_dataset(dataset_path)
        if d_errors:
            print(f"Dataset has {len(d_errors)} validation error(s). First 3:")
            for e in d_errors[:3]:
                print(f"  - {e}")
            sys.exit(1)

        pred_rows = read_jsonl(predictions_path)
    except (FileNotFoundError, ValueError) as ex:
        print(f"Error: {ex}", file=sys.stderr)
        sys.exit(1)

    result, missed = score(dataset_rows, pred_rows)

    print("\nSignalEval Score Summary")
    print("=" * 40)
    print(f"Dataset rows:         {result.total_dataset_rows}")
    print(f"Prediction rows:      {result.total_prediction_rows}")
    print(f"Matched rows:         {result.matched_rows}")
    print(f"Coverage:             {result.coverage * 100:.1f}%")
    print(f"Invalid predictions:  {result.invalid_prediction_count}")
    print("---")
    print(f"Direction accuracy:   {result.direction_accuracy * 100:.1f}%")
    print(f"Event type accuracy:  {result.event_type_accuracy * 100:.1f}%")
    print(f"Time horizon acc:     {result.time_horizon_accuracy * 100:.1f}%")
    print(f"Confidence match:     {result.confidence_match * 100:.1f}%")
    print("---")
    print(f"Macro score:          {result.macro_score * 100:.1f}%")

    if hasattr(args, "json_output") and args.json_output:
        import dataclasses
        out = Path(args.json_output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(dataclasses.asdict(result), indent=2) + "\n")
        print(f"\nMetrics written to {out}")


def cmd_report(args):
    from .report import generate_report

    dataset_path = Path(args.dataset)
    predictions_path = Path(args.predictions)
    output_path = Path(args.output)

    try:
        report_text = generate_report(dataset_path, predictions_path, output_path)
    except (FileNotFoundError, ValueError) as ex:
        print(f"Error: {ex}", file=sys.stderr)
        sys.exit(1)

    print(f"Report written to {output_path}")


def cmd_board(args):
    from .board import load_runs_from_dir, build_leaderboard, write_site
    from datetime import datetime

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    try:
        entries, warnings = load_runs_from_dir(input_dir)
    except (FileNotFoundError, ValueError) as ex:
        print(f"Error: {ex}", file=sys.stderr)
        sys.exit(1)

    for w in warnings:
        print(f"Warning: {w}", file=sys.stderr)

    rows = build_leaderboard(entries)
    generated_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M UTC")

    try:
        write_site(rows, output_dir, generated_at)
    except OSError as ex:
        print(f"Error writing output: {ex}", file=sys.stderr)
        sys.exit(1)

    print(f"Board generated: {output_dir / 'index.html'}")
    print(f"  Runs included: {len(rows)}")
    print(f"  CSS:           {output_dir / 'assets' / 'style.css'}")
    print(f"  Data:          {output_dir / 'data' / 'leaderboard.json'}")


def cmd_providers(args):
    print("\nSignalEval Providers\n" + "=" * 40)
    providers_info = [
        ("file",      "No API key required",              "Read predictions from an existing JSONL file"),
        ("mock",      "No API key required",              "Deterministic fake predictions for testing/demos"),
        ("ollama",    "Local Ollama server required",     "Local model via Ollama (localhost:11434)"),
        ("openai",    "OPENAI_API_KEY env var required",  "OpenAI chat completions API"),
        ("anthropic", "ANTHROPIC_API_KEY env var required", "Anthropic Messages API"),
    ]
    for name, req, desc in providers_info:
        print(f"  {name:<12} {req}")
        print(f"             {desc}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="signaleval",
        description="SignalEval Runner — financial news-to-signal model evaluation CLI",
    )
    parser.add_argument("--version", action="version", version=f"SignalEval Runner {__version__}")

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # init
    p_init = sub.add_parser("init", help="Initialize config and output folders")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing config")
    p_init.set_defaults(func=cmd_init)

    # validate
    p_val = sub.add_parser("validate", help="Validate a dataset JSONL file")
    p_val.add_argument("--dataset", required=True, help="Path to dataset JSONL")
    p_val.set_defaults(func=cmd_validate)

    # run
    p_run = sub.add_parser("run", help="Run a provider and generate predictions")
    p_run.add_argument("--dataset", required=True, help="Path to dataset JSONL")
    p_run.add_argument("--provider", required=True, help="Provider name: file, mock, ollama, openai, anthropic")
    p_run.add_argument("--output", required=True, help="Output predictions JSONL path")
    p_run.add_argument("--predictions-file", default="", help="Path to predictions file (for file provider)")
    p_run.add_argument("--model", default="", help="Model name (for ollama/openai/anthropic providers)")
    p_run.set_defaults(func=cmd_run)

    # score
    p_score = sub.add_parser("score", help="Score predictions against a dataset")
    p_score.add_argument("--dataset", required=True, help="Path to dataset JSONL")
    p_score.add_argument("--predictions", required=True, help="Path to predictions JSONL")
    p_score.add_argument("--json-output", default="", help="Optional: write metrics to JSON file")
    p_score.set_defaults(func=cmd_score)

    # report
    p_report = sub.add_parser("report", help="Generate a Markdown evaluation report")
    p_report.add_argument("--dataset", required=True, help="Path to dataset JSONL")
    p_report.add_argument("--predictions", required=True, help="Path to predictions JSONL")
    p_report.add_argument("--output", required=True, help="Output Markdown report path")
    p_report.set_defaults(func=cmd_report)

    # providers
    p_prov = sub.add_parser("providers", help="List supported providers")
    p_prov.set_defaults(func=cmd_providers)

    # board
    p_board = sub.add_parser("board", help="Generate static HTML leaderboard from run JSON files")
    p_board.add_argument("--input", required=True, help="Directory containing run result JSON files")
    p_board.add_argument("--output", required=True, help="Output directory for generated site")
    p_board.set_defaults(func=cmd_board)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
