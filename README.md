# AI Agent Identity and Authorization Security Lab

[![AgentIAM Verification](https://github.com/AAH20/ai-agent-identity-authorization-security/actions/workflows/verify.yml/badge.svg)](https://github.com/AAH20/ai-agent-identity-authorization-security/actions/workflows/verify.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

**AgentIAM Lab** is an open conformance suite for **AI agent identity**, **AI agent authorization**, **MCP authorization**, delegated access, workload identity, non-human identity security and accountable agent actions.

It answers a narrow enterprise question with executable evidence:

> Can this agent prove who authorized it, use only the authority required for this task, and leave a verifiable record of what happened?

> **Scope:** v0.1 is a deterministic reference lab, not a production identity provider or certification. Its local HMAC receipts prove shared-secret integrity only. They explicitly do not claim public-key non-repudiation.

## Why AgentIAM Lab

Traditional service identities assume predictable code and static permissions. AI agents can choose tools, create child agents and alter execution paths at runtime. A valid login therefore does not establish that the current action serves the approved intent.

The lab tests the complete decision context:

```text
principal + agent + delegation chain + intent + audience
          + resource + action + runtime context + approval
```

## Five executable conformance scenarios

| ID | Scenario | Required result |
|---|---|---|
| AIA-ID-001 | Human delegates one task to an agent | Principal, agent, intent, resources, actions and expiry remain distinct |
| AIA-AUTHN-001 | Broker issues a five-minute task token | Audience, resource, action and proof-of-possession binding retained |
| AIA-MCP-001 | Agent calls an MCP resource | Valid call succeeds; wrong audience and stolen bearer fail |
| AIA-DELEG-001 | Child asks for additional authority | Authority amplification fails closed |
| AIA-REV-001 | Owner revokes the parent | Parent and descendant authority stop immediately |

## Run it

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
agentiam test --json reports/conformance.json --junit reports/junit.xml
```

Or with Docker:

```bash
docker compose run --build conformance
```

## GitHub Action

```yaml
- uses: AAH20/ai-agent-identity-authorization-security@v1
  with:
    json-report: reports/agentiam.json
    junit-report: reports/agentiam.xml
```

The action currently runs the portable core conformance suite. Cloud and identity-provider adapters will add environment-specific tests.

## Reference authorization flow

```text
Human or service principal
           │
           ▼
Purpose-bound delegation
           │
           ▼
Agent identity broker ───── policy decision
           │
           ▼
Five-minute, task-scoped, key-bound token
           │
           ▼
AI agent or child agent
           │
           ▼
MCP server, API or cloud resource
           │
           ▼
Decision + integrity receipt + assurance evidence
```

## Implemented controls

- Unique parent and child agent identities
- Human or service principal attribution
- Purpose and intent retention
- Default maximum five-minute task-token lifetime
- Resource and action scopes
- Audience restriction
- Proof-of-possession check
- No child authority amplification
- Cascading delegation revocation
- Existing-token denial after revocation
- Token and result hashing in receipts
- Explicit distinction between integrity and non-repudiation
- OPA reference policy

## Vulnerable and controlled examples

[`lab/vulnerable_agent.py`](lab/vulnerable_agent.py) demonstrates a shared bearer key that grants every resource and action. [`lab/secure_agent.py`](lab/secure_agent.py) uses a purpose-bound delegation and a task-scoped token.

These examples are intentionally small. They expose the control difference without pretending the reference broker is a production OAuth authorization server.

## Authorization receipt

The machine-readable receipt records:

- Agent and accountable principal
- Parent delegation
- Business intent
- Audience, resource and action
- Policy decision
- Hashed token identifier
- Hashed result
- Timestamp
- Integrity method
- Whether the method supports non-repudiation

See [`schemas/authorization-receipt.schema.json`](schemas/authorization-receipt.schema.json).

## Standards traceability

The roadmap covers:

- NIST AI Agent Standards Initiative
- NIST NCCoE agent identity and authorization concept
- OAuth 2.1 and token exchange
- OpenID AuthZEN approval and MCP authorization profiles
- MCP authorization
- SPIFFE/SPIRE workload identity
- OPA and Cedar policy engines
- OWASP Top 10 for Agentic Applications 2026
- ISO/IEC 42001, NIST AI RMF and AIUC-1 evidence mappings

Traceability is not certification or protocol conformance. See [standards and adapters](docs/STANDARDS_AND_ADAPTERS.md).

## KPIs and unit economics

The project defines identity, authorization, delegation, operational and commercial measures in [KPIs and unit economics](docs/KPIS_AND_UNIT_ECONOMICS.md).

Primary release gates:

| KPI | Target |
|---|---:|
| Unauthorized action rate | 0% |
| Authority amplification rate | 0% |
| Cross-tenant access | 0 |
| Approval enforcement | 100% |
| Expired and revoked credential rejection | 100% |
| Complete delegation-chain coverage | 100% |
| Receipt integrity verification | 100% |

## Relationship to the AI Agent Security Trust Center

AgentIAM generates identity and authorization evidence. The Trust Center distributes approved assurance results to customers, auditors and GRC platforms.

```text
AgentIAM conformance evidence
             ↓
AI Agent Security Trust Center
             ↓
Customer, auditor, GRC and executive review
```

## Roadmap

- **v0.2:** MCP protected-resource metadata and token-exchange fixture
- **v0.3:** SPIFFE/SPIRE and Kubernetes workload identity adapter
- **v0.4:** AWS STS and GitHub OIDC adapter
- **v0.5:** AuthZEN request/approval and tool-authorization adapter
- **v0.6:** asymmetric receipt signatures and offline public verification
- **v0.7:** Cedar policy pack and multi-tenant test environment
- **v1.0:** independently reviewed conformance profile and signed evidence exports

## Security

Use only synthetic or explicitly authorized systems. Never use the vulnerable fixture in production. Report vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

## License

Apache-2.0. Standards and trademarks belong to their respective owners.
