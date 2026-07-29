# Implementation guide

## Mapping the proposal to runnable components

| SDLC step | Implementation | Runtime artifact |
|---|---|---|
| Intake | `Workflow._intake` validates the ticket and applies configurable risk policy | `risk_assessment` |
| Clarify | `RequirementsAgent` normalizes criteria and identifies explicit ambiguity | `requirements_contract` |
| Ground | `ContextAgent` inventories approved local sources with revision and SHA-256 provenance | `context_manifest` |
| Plan | `PlanningAgent` generates a bounded plan and rollback instruction | `implementation_plan` |
| Approve | `Workflow.approve` requires an attributed human decision for configured risk tiers | approval event |
| Implement | The reference adapter emits a Codex-ready brief but intentionally does not edit arbitrary repositories | `implementation_brief` |
| Verify | `QualityAgent` runs only exact commands in `config/workflow.json` | `quality_report` |
| Security | `SecurityAgent` creates scenario-specific findings and enforces a high-risk gate | `security_report` |
| Review | `ReviewAgent` maps criteria to evidence and hard-codes merge/deploy to false | `review_packet` |
| Learn | File-backed events and artifacts are available through CLI and API for metric export | run JSON |

The implementation is deliberately dependency-free at runtime. Its agents are deterministic adapters, making orchestration, policy, evidence, UI, and failure behavior demonstrable without credentials. Replace one adapter at a time with an approved Codex or enterprise integration while preserving its input/output contract.

## Production integration seams

1. Implement a model gateway that accepts the existing agent contract, validates structured output, records model/configuration identifiers, and redacts telemetry.
2. Replace the implementation brief with a worktree adapter that creates a short-lived branch and invokes Codex with the approved plan. Keep merge and deploy outside that tool's permissions.
3. Replace the fixture with a delegated-identity backlog connector.
4. Send verification to CI and attach signed results rather than treating local output as authoritative.
5. Move state to an append-only database/object store and authenticate every approval.

Do not connect customer repositories or data until threat modeling, retention, access control, and incident response have been reviewed.
