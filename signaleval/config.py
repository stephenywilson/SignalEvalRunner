import json
from pathlib import Path
from typing import Optional

DEFAULT_CONFIG = {
    "version": "0.1.0",
    "default_provider": "mock",
    "default_output_dir": ".signaleval/outputs",
    "default_report_dir": ".signaleval/reports",
}

SIGNALEVAL_DIR = Path(".signaleval")
CONFIG_PATH = SIGNALEVAL_DIR / "config.json"


def init_config(force: bool = False) -> bool:
    if CONFIG_PATH.exists() and not force:
        print(f"Config already exists at {CONFIG_PATH}. Use --force to overwrite.")
        return False

    SIGNALEVAL_DIR.mkdir(parents=True, exist_ok=True)
    (SIGNALEVAL_DIR / "outputs").mkdir(parents=True, exist_ok=True)
    (SIGNALEVAL_DIR / "reports").mkdir(parents=True, exist_ok=True)

    CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n", encoding="utf-8")
    print(f"Initialized SignalEval config at {CONFIG_PATH}")
    print(f"Created directories: {SIGNALEVAL_DIR}/outputs/, {SIGNALEVAL_DIR}/reports/")
    return True


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()
