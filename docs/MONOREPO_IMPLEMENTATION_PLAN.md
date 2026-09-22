# Monorepo Implementation Plan

## Proposed structure

```text
sovereign-identity-trust-fabric/
├── apps/
│   ├── admin-console/                 # community operator UI
│   ├── verifier-portal/               # local evidence inspection
│   └── demo-control-room/              # reproducible human/agent/robot scenarios
├── packages/
│   ├── contracts/                     # identity, delegation, receipt and event schemas
│   ├── identity-graph/                # normalized entities and relationships
│   ├── delegation-engine/             # parent/child authority and revocation
│   ├── policy-pep/                    # enforcement-point SDK
│   ├── token-broker/                  # short-lived, audience-bound credentials
│   ├── pam-reference/                 # synthetic target and JIT/JEA example
│   ├── context-guard/                 # authorization-preserving RAG contract
│   ├── evidence-sdk/                  # signed receipt creation and verification
│   ├── grc-claw-bridge/               # control mappings and assurance envelopes
│   └── robot-black-box-bridge/         # physical-action receipt compatibility
├── adapters/
│   ├── oidc/
│   ├── scim/
│   ├── spiffe/
│   ├── opa/
│   ├── cedar/
│   ├── mcp/
│   ├── kubernetes/
│   ├── langgraph/
│   ├── cognee/
│   └── obsidian-local/
├── policies/
│   ├── workforce/
│   ├── privileged-access/
│   ├── agent-delegation/
│   ├── biometric-purpose/
│   ├── rag-retrieval/
│   └── physical-ai/
├── conformance/
│   ├── profiles/
│   ├── attack-fixtures/
│   ├── test-vectors/
│   └── reports/
├── schemas/
│   ├── identity/
│   ├── delegation/
│   ├── authorization/
│   ├── action-receipt/
│   └── assurance-envelope/
├── deploy/
│   ├── compose/
│   ├── kubernetes/
│   └── airgap-reference/
├── examples/
│   ├── employee-admin-jit/
│   ├── agent-mcp-delegation/
│   ├── biometric-step-up/
│   ├── governed-rag/
│   └── robot-action-black-box/
├── docs/
│   ├── architecture/
│   ├── threat-model/
│   ├── standards/
│   ├── egypt-profile/
│   └── commercial-boundary/
└── commercial-manifest.example.yaml   # public declaration of non-OSS capabilities
```

## What to reuse now

| Existing asset | Role in the monorepo |
|---|---|
| AgentIAM Lab | Seed for contracts, delegation engine, broker and conformance suite |
| GRC Claw | Governance mappings, evidence graph, assurance envelopes and audit exports |
| Robot Black Box | Physical-action recording, replay and outcome evidence |
| Existing OPA policy | First default-deny delegation policy |
| Authorization receipt schema | Base event contract to version rather than replace |

## First 90 days

### Days 0-30: freeze the contract

- Move the current receipt and delegation models into versioned schemas.
- Add public-key signatures, key identifiers, rotation and revocation fixtures.
- Define identity types for person, workload, agent, model, device and robot.
- Publish a provider-neutral adapter interface and compatibility test kit.
- Build one end-to-end scenario: employee delegates a constrained MCP task, the task accesses an authorized RAG source, and GRC Claw verifies the receipt.

### Days 31-60: prove interoperability

- Add OIDC/SCIM, SPIFFE, OPA and Cedar reference adapters.
- Add revocation propagation, tenant-isolation and replay tests.
- Connect the Robot Black Box receipt vocabulary.
- Add a synthetic biometric step-up adapter that never stores real biometric data.
- Export events to local Iceberg tables and render evidence freshness and lineage.

### Days 61-90: create the commercial wedge

- Run a controlled enterprise pilot with one identity provider, one privileged target and one agent framework.
- Produce an Egyptian deployment profile covering localization, residency, evidence and operator roles.
- Package an architecture diagnostic, controlled pilot and annual platform proposal.
- Recruit one system integrator as a delivery partner under a non-exclusive agreement.
- Commission independent cryptographic and tenant-isolation review before production claims.

## Initial reference demonstrations

1. **Agent escalation denied:** a child agent requests broader cloud authority; the broker rejects it and GRC Claw produces the evidence packet.
2. **Privileged session with purpose:** an engineer receives a 15-minute production entitlement; commands outside the approved change fail.
3. **Governed biometric step-up:** a synthetic biometric provider returns a high-assurance result, but access still fails when purpose or consent evidence is missing.
4. **Authorization-preserving RAG:** an agent can retrieve permitted Obsidian/Cognee material while restricted source chunks remain unreachable after indexing.
5. **Robot action accountability:** a simulated VLA action is linked to the operator, model, policy, digital-twin test and resulting telemetry in Robot Black Box.
6. **Succession and recovery:** one key custodian becomes unavailable; quorum recovery rotates the issuer without bypassing tenant controls.

## Production gates

- External threat model and cryptographic review.
- Reproducible builds, signed releases, SBOM and dependency provenance.
- HA and disaster-recovery tests with declared RTO and RPO.
- Tenant-isolation tests at API, storage, queue, cache and analytics layers.
- Policy rollback and emergency suspension exercises.
- Privacy impact assessment for biometric or surveillance integrations.
- Hardware-independent safety case for physical AI integrations.
- Measured load, authorization latency, revocation latency and evidence durability.
- Clear support ownership and incident-response escalation.

