from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .server import serve
from .workflow import Workflow


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Run the Agentic SDLC Control Tower locally")
    result.add_argument("--repo", type=Path, default=Path.cwd(), help="Repository root")
    result.add_argument("--config", type=Path, default=Path("config/workflow.json"))
    commands = result.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run", help="Start a ticket and execute until an approval gate")
    run.add_argument("ticket", type=Path)
    status = commands.add_parser("status", help="Show a persisted run")
    status.add_argument("run_id")
    approve = commands.add_parser("approve", help="Record a human approval and continue")
    approve.add_argument("run_id")
    approve.add_argument("--gate", required=True, choices=["plan", "security"])
    approve.add_argument("--by", required=True, dest="approver")
    web = commands.add_parser("serve", help="Start the local dashboard and JSON API")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", default=8080, type=int)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    repository = args.repo.resolve()
    config = args.config if args.config.is_absolute() else repository / args.config
    workflow = Workflow.from_config(repository, config)
    try:
        if args.command == "run":
            ticket = json.loads(args.ticket.read_text(encoding="utf-8"))
            state = workflow.run_until_gate(workflow.start(ticket))
        elif args.command == "status":
            state = workflow.store.load(args.run_id)
        elif args.command == "approve":
            state = workflow.approve(workflow.store.load(args.run_id), args.gate, args.approver)
        else:
            serve(workflow, args.host, args.port)
            return 0
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(state.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
