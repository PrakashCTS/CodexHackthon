# Evaluation plan

## Experiment design

Compare the agent-assisted flow with a baseline group on sanitized historical tasks. Stratify by repository, risk, and complexity; pre-register success thresholds; and report median, p75, and confidence intervals.

Measure accepted lead time, active developer time, reviewer time, first-pass CI success, review rework, escaped defects, gate enforcement, source groundedness, cost, latency, and user trust. Speed cannot compensate for a quality or control regression.

## Automated acceptance checks

- High-risk tickets pause at plan and security gates.
- Approvals include identity and UTC time.
- Invalid tickets and traversal-like run identifiers are rejected.
- Every stage creates a typed evidence artifact.
- A review packet can never authorize merge or deployment.
- API health and full low-risk workflow succeed locally.
- Configured validation commands all return zero.

## Hackathon demo scorecard

| Dimension | Demonstration evidence |
|---|---|
| Business value | Baseline versus assisted cycle time and review effort |
| Technical completeness | One story reaches a review packet end to end |
| Responsible AI | Risk gates, injection boundary, provenance, no autonomous merge |
| Innovation | Intent-to-evidence continuity rather than isolated code completion |
| Scalability | Typed adapters, persisted state, CI integration seams |
| Presentation | Live dashboard plus recorded fallback and exact runbook |
