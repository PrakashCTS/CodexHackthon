import json
import tempfile
import unittest
from pathlib import Path

from control_tower.store import RunStore
from control_tower.workflow import Workflow


class WorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.config = {
            "risk": {"high_risk_terms": ["authentication"], "medium_risk_terms": ["api"]},
            "policy": {"require_plan_approval_for": ["high"], "require_security_approval_for": ["high"]},
            "tools": {"allowed_commands": [], "timeout_seconds": 5},
        }
        self.workflow = Workflow(self.root, self.config, RunStore(self.root / ".control-tower"))
        self.ticket = {"id": "T-1", "title": "Authentication change", "description": "authentication behavior", "acceptance_criteria": ["Works"]}

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_high_risk_run_stops_at_both_human_gates(self) -> None:
        state = self.workflow.run_until_gate(self.workflow.start(self.ticket))
        self.assertEqual("waiting_for_approval", state.status)
        self.assertEqual("approve_plan", state.current_stage)
        state = self.workflow.approve(state, "plan", "architect@example.test")
        self.assertEqual("security", state.current_stage)
        self.assertEqual("waiting_for_approval", state.status)
        state = self.workflow.approve(state, "security", "security@example.test")
        self.assertEqual("completed", state.status)
        self.assertEqual("complete", state.current_stage)
        self.assertEqual(1, sum(item["kind"] == "security_report" for item in state.artifacts))
        review = next(item for item in state.artifacts if item["kind"] == "review_packet")
        self.assertFalse(review["data"]["merge_allowed"])

    def test_store_rejects_path_traversal(self) -> None:
        with self.assertRaises(ValueError):
            self.workflow.store.load("../../etc/passwd")

    def test_ticket_requires_identity_title_and_description(self) -> None:
        with self.assertRaisesRegex(ValueError, "description"):
            self.workflow.start({"id": "T-2", "title": "Incomplete"})


if __name__ == "__main__":
    unittest.main()
