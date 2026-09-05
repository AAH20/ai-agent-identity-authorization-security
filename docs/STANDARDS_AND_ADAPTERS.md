# Standards and Adapter Plan

## Standards boundary

The core lab tests security properties. It does not claim certification against a draft, standard or vendor product. Every adapter must record protocol version, provider version, test date, configuration, evidence hashes and unsupported tests.

| Area | Reference | Planned implementation evidence |
|---|---|---|
| Agent identity | NIST AI Agent Standards Initiative and NCCoE concept paper | Unique identity, owner, purpose, instance and lifecycle tests |
| Delegated authorization | OAuth token exchange and on-behalf-of patterns | Principal, actor, audience, resources, actions and expiry |
| Externalized policy | OpenID AuthZEN | Access evaluation and approval prerequisite exchange |
| MCP authorization | MCP authorization and AuthZEN tool profile | Protected-resource discovery, scoped tokens and tool decisions |
| Workload identity | SPIFFE/SPIRE | Short-lived workload certificate and trust-domain enforcement |
| Cloud identity | AWS STS, Kubernetes and Entra adapters | Federated issuance, scope, revocation and audit evidence |
| Agent security | OWASP Agentic Top 10 | Injection-aware authorization, excessive-agency and tool misuse tests |
| Governance | NIST AI RMF, ISO 42001 and AIUC-1 | Traceable evidence mappings and accountable review |

## Adapter contract

An adapter receives a synthetic principal, agent definition, delegation, resource and requested action. It returns normalized issuance evidence, authorization decisions, revocation results, latency, cost, logs and failure diagnostics. Secrets must never enter the report.

An adapter result uses one status:

- `VERIFIED`: reproduced with retained, redacted evidence.
- `OBSERVED`: witnessed but not independently reproduced.
- `DOCUMENTED`: supported only by a dated first-party source.
- `NOT_SUPPORTED`: reproducible test establishes absence in the tested configuration.
- `NOT_TESTED`: no defensible result.

## Public-key receipt roadmap

v0.1 uses an HMAC only to test tamper detection inside one trust boundary. Because issuer and verifier share the same secret, it cannot establish non-repudiation. The public profile will support asymmetric organizational keys or Sigstore identity, trusted timestamps, key rotation, revocation and offline verification before claiming non-repudiation.
