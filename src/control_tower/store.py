from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from .models import RunState


class RunStore:
    """File-backed evidence store using atomic replacement for local durability."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.runs = root / "runs"
        self.runs.mkdir(parents=True, exist_ok=True)

    def save(self, state: RunState) -> None:
        target = self.runs / f"{state.run_id}.json"
        fd, temporary = tempfile.mkstemp(dir=self.runs, prefix=".run-", suffix=".json")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(state.to_dict(), stream, indent=2, sort_keys=True)
                stream.write("\n")
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def load(self, run_id: str) -> RunState:
        if not run_id.replace("-", "").isalnum():
            raise ValueError("Invalid run identifier")
        path = self.runs / f"{run_id}.json"
        if not path.exists():
            raise KeyError(f"Run not found: {run_id}")
        return RunState.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list(self) -> list[dict[str, object]]:
        summaries = []
        for path in sorted(self.runs.glob("*.json"), reverse=True):
            value = json.loads(path.read_text(encoding="utf-8"))
            summaries.append({key: value[key] for key in (
                "run_id", "status", "risk", "current_stage", "created_at", "updated_at"
            )})
        return summaries
