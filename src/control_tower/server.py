from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .workflow import Workflow


class ControlTowerServer(ThreadingHTTPServer):
    workflow: Workflow


class Handler(BaseHTTPRequestHandler):
    server: ControlTowerServer

    def do_GET(self) -> None:  # noqa: N802 - standard library handler API
        path = urlparse(self.path).path
        if path == "/":
            self._send(Path(__file__).with_name("static").joinpath("index.html").read_bytes(), "text/html; charset=utf-8")
        elif path == "/app.js":
            self._send(Path(__file__).with_name("static").joinpath("app.js").read_bytes(), "text/javascript; charset=utf-8")
        elif path == "/styles.css":
            self._send(Path(__file__).with_name("static").joinpath("styles.css").read_bytes(), "text/css; charset=utf-8")
        elif path == "/healthz":
            self._json({"status": "ok"})
        elif path == "/api/runs":
            self._json({"runs": self.server.workflow.store.list()})
        elif path.startswith("/api/runs/"):
            try:
                self._json(self.server.workflow.store.load(path.rsplit("/", 1)[-1]).to_dict())
            except (KeyError, ValueError) as error:
                self._json({"error": str(error)}, HTTPStatus.NOT_FOUND)
        else:
            self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802 - standard library handler API
        path = urlparse(self.path).path
        try:
            body = self._body()
            if path == "/api/runs":
                state = self.server.workflow.run_until_gate(self.server.workflow.start(body))
                self._json(state.to_dict(), HTTPStatus.CREATED)
            elif path.endswith("/approve") and path.startswith("/api/runs/"):
                run_id = path.split("/")[3]
                state = self.server.workflow.store.load(run_id)
                self._json(self.server.workflow.approve(state, body["gate"], body["approver"]).to_dict())
            else:
                self._json({"error": "not found"}, HTTPStatus.NOT_FOUND)
        except (KeyError, ValueError, json.JSONDecodeError) as error:
            self._json({"error": str(error)}, HTTPStatus.BAD_REQUEST)

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 1_000_000:
            raise ValueError("Request body exceeds 1 MB")
        return json.loads(self.rfile.read(length))

    def _json(self, value: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        self._send(json.dumps(value).encode(), "application/json; charset=utf-8", status)

    def _send(self, body: bytes, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; connect-src 'self'; style-src 'self'")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"control-tower: {fmt % args}")


def serve(workflow: Workflow, host: str, port: int) -> None:
    server = ControlTowerServer((host, port), Handler)
    server.workflow = workflow
    print(f"Agentic SDLC Control Tower: http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
