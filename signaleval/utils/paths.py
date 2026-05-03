from pathlib import Path


def resolve_output_path(path: str, default_dir: str = ".signaleval/outputs") -> Path:
    p = Path(path)
    if not p.is_absolute() and not str(path).startswith(".") and "/" not in str(path):
        p = Path(default_dir) / path
    return p


def ensure_dir(path: Path) -> Path:
    Path(path).mkdir(parents=True, exist_ok=True)
    return Path(path)
