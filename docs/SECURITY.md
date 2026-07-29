# Security and governance model

## Local boundary

This prototype binds to loopback by default, has no authentication, and is intended only for a trusted developer workstation. Do not expose it to a shared network. Its UI uses same-origin assets, limits JSON bodies to 1 MB, validates run identifiers, and adds restrictive browser headers.

The local agents cannot merge or deploy. The implementation stage produces a brief instead of running an unconstrained coding tool. Verification commands are administrator-owned configuration and execute without a shell.

## Threats and controls

| Threat | Current control | Production requirement |
|---|---|---|
| Prompt injection | Retrieved content is metadata, not executable instruction | Content boundary labels and adversarial model evaluation |
| Command injection | Exact configured allow-list; no shell | Signed policy bundle and isolated runner |
| Unauthorized approval | Attribution recorded for demonstration | SSO, delegated identity, RBAC, MFA for critical gates |
| Path traversal | Restricted run identifier and controlled static paths | Gateway normalization and security tests |
| Source/data leakage | Local-only operation and no external model call | Classification, DLP, encryption, retention and egress policy |
| Evidence tampering | Atomic local writes | Append-only remote store, signatures and independent audit account |

## Production go/no-go

Require a threat model, privacy review, abuse cases, code-owner approval, dependency/SBOM scan, secrets scan, penetration test, incident playbook, backup/restore test, observability redaction review, and evaluation-gate sign-off before a pilot.
