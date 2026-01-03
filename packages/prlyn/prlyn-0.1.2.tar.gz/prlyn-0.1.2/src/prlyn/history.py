import os
import json
import hashlib
from typing import Optional
from prlyn.models import AnalysisResult

HISTORY_DIR = ".prlyn"


def save_analysis(result: AnalysisResult):
    """Saves analysis result to .prlyn/ directory based on prompt hash."""
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

    prompt_hash = hashlib.md5(result.raw_text.encode()).hexdigest()
    file_path = os.path.join(HISTORY_DIR, f"{prompt_hash}.json")

    with open(file_path, "w") as f:
        f.write(result.model_dump_json(indent=2))


def get_previous_analysis(raw_text: str) -> Optional[dict]:
    """Retrieves the last saved analysis for a given prompt (mocked by using the same hash)."""
    # Note: Real implementation might track history over time with timestamps.
    # For now, we'll look for a file by hash.
    if not os.path.exists(HISTORY_DIR):
        return None

    prompt_hash = hashlib.md5(raw_text.encode()).hexdigest()
    file_path = os.path.join(HISTORY_DIR, f"{prompt_hash}.json")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return None


def find_latest_history() -> Optional[dict]:
    """Finds the most recently modified history file."""
    if not os.path.exists(HISTORY_DIR):
        return None

    files = [
        os.path.join(HISTORY_DIR, f)
        for f in os.listdir(HISTORY_DIR)
        if f.endswith(".json")
    ]
    if not files:
        return None

    latest_file = max(files, key=os.path.getmtime)
    with open(latest_file, "r") as f:
        return json.load(f)
