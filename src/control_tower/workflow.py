from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from .agents import ContextAgent, PlanningAgent, QualityAgent, RequirementsAgent, ReviewAgent, SecurityAgent
from .models import RunState, utc_now
from .store import RunStore


STAGES = ["intake", "clarify", "ground", "plan", "approve_plan", "implement", "verify", "security", "review", "complete"]


class ApprovalRequired(RuntimeError):
    pass


class Workflow:
    def __init__(self, repository: Path, config: dict[str, Any], store: RunStore) -> None:
        self.repository = repository.resolve()
        self.config = config
        self.store = store

    @classmethod
    def from_config(cls, repository: Path, config_path: Path) -> "Workflow":
        config = json.loads(config_path.read_text(encoding="utf-8"))
        workspace = repository / config["workspace"]
        return cls(repository, config, RunStore(workspace))

    def start(self, ticket: dict[str, Any]) -> RunState:
        self._validate_ticket(ticket)
        state = RunState(run_id=uuid.uuid4().hex[:12], ticket=ticket)
        state.event("run_created", f"Created run for {ticket['id']}")
        self.store.save(state)
        return state

    def run_until_gate(self, state: RunState) -> RunState:
        while state.current_stage != "complete":
            if state.status == "waiting_for_approval":
                break
            self.step(state)
        return state

    def step(self, state: RunState) -> RunState:
        handlers = {
            "intake": self._intake, "clarify": self._clarify, "ground": self._ground,
            "plan": self._plan, "approve_plan": self._approve_plan,
            "implement": self._implement, "verify": self._verify,
            "security": self._security, "review": self._review,
        }
        if state.current_stage == "complete":
            return state
        state.status = "running"
        handlers[state.current_stage](state)
        self.store.save(state)
        return state

    def approve(self, state: RunState, gate: str, approver: str) -> RunState:
        if gate not in state.required_approvals:
            raise ValueError(f"Approval is not required for gate: {gate}")
        if not approver.strip():
            raise ValueError("Approver identity is required")
        state.approvals[gate] = {"approver": approver, "approved_at": utc_now()}
        state.event("approval_recorded", f"{gate} approved", approver=approver)
        state.status = "running"
        self.store.save(state)
        return self.run_until_gate(state)

    def _advance(self, state: RunState, next_stage: str) -> None:
        state.event("stage_completed", f"Completed {state.current_stage}")
        state.current_stage = next_stage

    def _intake(self, state: RunState) -> None:
        text = " ".join([state.ticket.get("title", ""), state.ticket.get("description", ""), *state.ticket.get("labels", [])]).lower()
        high = self.config["risk"]["high_risk_terms"]
        medium = self.config["risk"]["medium_risk_terms"]
        state.risk = "high" if any(term in text for term in high) else "medium" if any(term in text for term in medium) else "low"
        state.artifact("intake", "risk_assessment", {"classification": state.risk, "method": "configured keyword policy"})
        self._advance(state, "clarify")

    def _clarify(self, state: RunState) -> None:
        state.artifact("clarify", "requirements_contract", RequirementsAgent().run(state.ticket))
        self._advance(state, "ground")

    def _ground(self, state: RunState) -> None:
        state.artifact("ground", "context_manifest", ContextAgent().run(self.repository))
        self._advance(state, "plan")

    def _plan(self, state: RunState) -> None:
        state.artifact("plan", "implementation_plan", PlanningAgent().run(state.ticket, state.risk))
        if state.risk in self.config["policy"]["require_plan_approval_for"]:
            state.required_approvals.append("plan")
        self._advance(state, "approve_plan")

    def _approve_plan(self, state: RunState) -> None:
        if "plan" in state.required_approvals and "plan" not in state.approvals:
            state.status = "waiting_for_approval"
            state.event("approval_required", "Human plan approval is required", gate="plan")
            return
        self._advance(state, "implement")

    def _implement(self, state: RunState) -> None:
        state.artifact("implement", "implementation_brief", {
            "mode": "local-reference",
            "instructions": "Use Codex in an isolated worktree to execute the approved plan.",
            "executed": False,
            "reason": "This reference workflow never edits an arbitrary target repository automatically.",
        })
        self._advance(state, "verify")

    def _verify(self, state: RunState) -> None:
        report = QualityAgent().run(
            self.repository, self.config["tools"]["allowed_commands"],
            self.config["tools"]["timeout_seconds"],
        )
        state.artifact("verify", "quality_report", report)
        if not report["passed"]:
            state.status = "failed"
            state.event("checks_failed", "One or more allow-listed checks failed")
            state.current_stage = "complete"
            return
        self._advance(state, "security")

    def _security(self, state: RunState) -> None:
        if not any(item["kind"] == "security_report" for item in state.artifacts):
            report = SecurityAgent().run(state.ticket, state.risk)
            state.artifact("security", "security_report", report)
        if state.risk in self.config["policy"]["require_security_approval_for"]:
            if "security" not in state.required_approvals:
                state.required_approvals.append("security")
            if "security" not in state.approvals:
                state.status = "waiting_for_approval"
                state.event("approval_required", "Human security approval is required", gate="security")
                return
        self._advance(state, "review")

    def _review(self, state: RunState) -> None:
        state.artifact("review", "review_packet", ReviewAgent().run(state.ticket, state.artifacts))
        state.status = "completed"
        self._advance(state, "complete")

    @staticmethod
    def _validate_ticket(ticket: dict[str, Any]) -> None:
        missing = [key for key in ("id", "title", "description") if not ticket.get(key)]
        if missing:
            raise ValueError(f"Ticket is missing required fields: {', '.join(missing)}")
