# Local runbook

## Prerequisites

- Python 3.11 or later
- Git
- Optional: Docker with Compose

No API key or third-party Python dependency is required for the local reference flow.

## Native setup and dashboard

```bash
make install
make test
make serve
```

Open <http://127.0.0.1:8080>, select **Start demo run**, and approve the plan and security gates. Run state is written under `.control-tower/runs/` and is ignored by Git.

## CLI walkthrough

```bash
make demo
# Copy run_id from the output, then:
PYTHONPATH=src python -m control_tower.cli status RUN_ID
PYTHONPATH=src python -m control_tower.cli approve RUN_ID --gate plan --by architect@example.com
PYTHONPATH=src python -m control_tower.cli approve RUN_ID --gate security --by security@example.com
```

The final review packet must report `merge_allowed: false` and `deployment_allowed: false`.

## Docker

```bash
docker compose up --build
curl http://127.0.0.1:8080/healthz
docker compose down
```

The Compose service is read-only, drops Linux capabilities, prevents privilege escalation, and persists only the evidence volume.

## Configuration

Edit `config/workflow.json` to change risk terms, mandatory gates, exact allow-listed validation commands, timeouts, and workspace. Never add a shell expression or user-controlled command. The runner tokenizes configured commands and does not invoke a shell.

## Troubleshooting and cleanup

- Port conflict: pass `--port 8090` directly to the CLI.
- Failed checks: inspect the `quality_report` in run JSON and rerun after correcting the environment.
- Reset demo evidence: run `make clean`.
- Health probe: `curl --fail http://127.0.0.1:8080/healthz`.
