import json
from pathlib import Path
from src.models.result import EvaluationResult

DATA_FILE = Path("data/results.json")


def save_result(result: EvaluationResult) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = []

    data.append(result.model_dump())

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)