from pathlib import Path
from typing import List

from .utils.jsonl import read_jsonl, write_jsonl
from .validate import validate_dataset


def run_provider(dataset_path: Path, provider_name: str, output_path: Path, **provider_kwargs) -> int:
    from .providers import get_provider

    dataset_rows, errors = validate_dataset(dataset_path)
    if errors:
        print(f"Dataset validation failed with {len(errors)} error(s). First few:")
        for e in errors[:5]:
            print(f"  - {e}")
        raise SystemExit(1)

    provider_cls = get_provider(provider_name)
    provider = provider_cls(**provider_kwargs)

    predictions = []
    print(f"Running provider '{provider_name}' on {len(dataset_rows)} rows...")
    for i, row in enumerate(dataset_rows):
        try:
            pred = provider.predict(row)
            predictions.append(pred)
        except Exception as ex:
            print(f"  Warning: provider error on row {row.get('id', i)}: {ex}")
            continue

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_path, predictions)
    print(f"Wrote {len(predictions)} predictions to {output_path}")
    return len(predictions)
