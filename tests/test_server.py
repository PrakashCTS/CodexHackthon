import json
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

from control_tower.server import ControlTowerServer, Handler
from control_tower.store import RunStore
from control_tower.workflow import Workflow


class ServerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        root = Path(self.temporary.name)
        config = {"risk": {"high_risk_terms": [], "medium_risk_terms": []}, "policy": {"require_plan_approval_for": [], "require_security_approval_for": []}, "tools": {"allowed_commands": [], "timeout_seconds": 5}}
        self.server = ControlTowerServer(("127.0.0.1", 0), Handler)
        self.server.workflow = Workflow(root, config, RunStore(root / "state"))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.temporary.cleanup()

    def test_health_and_run_api(self) -> None:
        base = f"http://127.0.0.1:{self.server.server_port}"
        with urllib.request.urlopen(f"{base}/healthz") as response:
            self.assertEqual({"status": "ok"}, json.load(response))
        ticket = json.dumps({"id": "T-3", "title": "Docs", "description": "Update docs"}).encode()
        request = urllib.request.Request(f"{base}/api/runs", ticket, {"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request) as response:
            state = json.load(response)
        self.assertEqual("completed", state["status"])


if __name__ == "__main__":
    unittest.main()
