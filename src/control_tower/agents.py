from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path
from typing import Any


class RequirementsAgent:
    def run(self, ticket: dict[str, Any]) -> dict[str, Any]:
        criteria = ticket.get("acceptance_criteria", [])
        questions = []
        if "requires product confirmation" in ticket.get("description", "").lower():
            questions.append("Confirm reset and unlock behavior with the product owner.")
        return {
            "ticket_id": ticket["id"],
            "acceptance_criteria": criteria,
            "non_functional_requirements": ticket.get("non_functional_requirements", []),
            "blocking_questions": questions,
            "definition_of_ready": bool(criteria),
        }


class ContextAgent:
    def run(self, repository: Path) -> dict[str, Any]:
        candidates = ["README.md", "AGENTS.md", "pyproject.toml", "config/workflow.json"]
        sources = []
        for relative in candidates:
            path = repository / relative
            if path.is_file():
                content = path.read_bytes()
                sources.append({
                    "path": relative, "sha256": hashlib.sha256(content).hexdigest(),
                    "bytes": len(content), "provenance": "repository",
                })
        return {"revision": self._revision(repository), "sources": sources}

    @staticmethod
    def _revision(repository: Path) -> str:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repository, text=True,
            capture_output=True, check=False, timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else "unversioned"


class PlanningAgent:
    def run(self, ticket: dict[str, Any], risk: str) -> dict[str, Any]:
        return {
            "objective": ticket["title"],
            "risk": risk,
            "steps": [
                "Confirm all blocking requirement questions.",
                "Identify the smallest implementation boundary and existing tests.",
                "Implement the behavior in an isolated worktree.",
                "Add positive, negative, boundary, and regression tests.",
                "Run allow-listed quality and security checks.",
                "Create a requirement-to-evidence review packet.",
            ],
            "rollback": "Revert the isolated change; no merge or deployment is permitted locally.",
        }


class SecurityAgent:
    def run(self, ticket: dict[str, Any], risk: str) -> dict[str, Any]:
        findings = []
        description = ticket.get("description", "").lower()
        if "authentication" in description:
            findings.append({
                "severity": "medium",
                "control": "authentication-abuse",
                "recommendation": "Test threshold boundaries, concurrency, reset behavior, and log redaction.",
            })
        return {"risk": risk, "findings": findings, "approved": risk != "high"}


class QualityAgent:
    def run(self, repository: Path, commands: list[str], timeout: int) -> dict[str, Any]:
        results = []
        for command in commands:
            completed = subprocess.run(
                command.split(), cwd=repository, capture_output=True, text=True,
                timeout=timeout, check=False,
            )
            results.append({
                "command": command, "exit_code": completed.returncode,
                "stdout": completed.stdout[-4000:], "stderr": completed.stderr[-4000:],
            })
        return {"passed": all(item["exit_code"] == 0 for item in results), "checks": results}


class ReviewAgent:
    def run(self, ticket: dict[str, Any], artifacts: list[dict[str, Any]]) -> dict[str, Any]:
        evidence = [item["kind"] for item in artifacts]
        return {
            "title": f"Draft: {ticket['id']} — {ticket['title']}",
            "acceptance_criteria": [
                {"criterion": criterion, "evidence": "quality_report" if "quality_report" in evidence else "pending"}
                for criterion in ticket.get("acceptance_criteria", [])
            ],
            "artifact_types": evidence,
            "merge_allowed": False,
            "deployment_allowed": False,
        }
