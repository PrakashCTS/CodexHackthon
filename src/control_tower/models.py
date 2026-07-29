from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Artifact:
    stage: str
    kind: str
    data: dict[str, Any]
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RunState:
    run_id: str
    ticket: dict[str, Any]
    status: str = "created"
    risk: str = "unknown"
    current_stage: str = "intake"
    required_approvals: list[str] = field(default_factory=list)
    approvals: dict[str, dict[str, str]] = field(default_factory=dict)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def event(self, event_type: str, message: str, **details: Any) -> None:
        self.events.append({
            "timestamp": utc_now(), "type": event_type,
            "message": message, "details": details,
        })
        self.updated_at = utc_now()

    def artifact(self, stage: str, kind: str, data: dict[str, Any]) -> None:
        self.artifacts.append(Artifact(stage, kind, data).to_dict())
        self.updated_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "RunState":
        return cls(**value)
