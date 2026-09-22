# Open Core and Commercial Boundary

## Boundary rule

The public project must make security claims independently testable and integrations possible without permission. The commercial layer sells production operation, regulated assurance, scale, proprietary connectors and accountable service levels.

If a feature is required to verify that the system is safe, it belongs in the open core. If it primarily reduces enterprise operating cost, integrates a proprietary estate, or transfers operational responsibility to A2Z SOC, it may be commercial.

## Exact product boundary

| Capability | Open project | Commercial A2Z SOC layer |
|---|---|---|
| Schemas | Identity, delegation, policy request, receipt and evidence schemas | Schema registry service, compatibility guarantees and migration automation |
| Conformance | Local deterministic tests, attack fixtures and public score format | Managed certification runs, signed registry, independent assessment coordination |
| Policy | Reference OPA/Cedar policies and policy test kit | Enterprise policy studio, approval workflow, simulation, rollout and rollback |
| Identity | SDK and reference OIDC, SCIM and SPIFFE adapters | Production Entra, Okta, Ping, Oracle, SAP, mainframe and national-ID connectors |
| PAM | Reference JIT token broker and synthetic target | HA vault integration, session proxy, credential rotation, command controls and recording |
| Agent IAM | Purpose-bound delegation, child constraints and MCP fixture | Fleet inventory, runtime gateway, multi-agent analytics and enterprise revocation plane |
| Physical AI | Receipt schema and simulated Robot Black Box bridge | Edge gateway, fleet operations, hardware attestation and supported robotics adapters |
| Biometrics | Abstract assurance-result interface and privacy test suite | Certified-vendor integrations, template-vault integration and deployment assurance; no resale of raw biometric data |
| Context and RAG | Authorization-preserving retrieval contract | Obsidian, Cognee, LangGraph and enterprise knowledge connectors with support |
| Evidence | Local signed receipts, verification CLI and GRC Claw export | Evidence vault, Apache Iceberg lakehouse, retention, legal hold, customer trust portal |
| Deployment | Docker Compose and reference Kubernetes manifests | Hardened Helm/operator, air-gap bundles, HSM/KMS, disaster recovery and upgrade service |
| Operations | Community documentation | 24x7 support, SLOs, incident response, managed identity operations and named assurance lead |
| Analytics | Transparent baseline metrics | Cross-tenant anonymized benchmarks, risk models, capacity planning and executive BI |

## Repository and license model

- Use Apache-2.0 for schemas, SDKs, conformance tests, reference policy packs and non-sensitive adapters.
- Keep trademarks, certification marks and the signed public conformance registry under controlled governance.
- Publish a contributor agreement and provenance policy for high-risk policy and cryptographic changes.
- Keep proprietary connectors, enterprise UI, HA control plane, deployment automation, benchmark corpus and managed service runbooks in private repositories.
- Never hide a security-critical verification step behind the commercial license.

This creates an adoption moat through compatibility and trust while preserving a commercial moat through operating data, integration depth, deployment expertise, assurance reputation and partner distribution.

## Commercial editions

Prices below are planning hypotheses in USD, excluding tax, hardware, third-party licenses and unusual travel. They require customer discovery and competitive validation before publication.

| Offer | Intended buyer | Included scope | Planning price |
|---|---|---|---:|
| Architecture diagnostic | CISO, CIO, regulator, investor | 2-4 week identity/privilege/agent assessment and roadmap | $25k-$60k one-time |
| Controlled pilot | Bank, telecom, operator, large enterprise | 8-12 week deployment, 3-5 integrations, evidence pack | $75k-$200k one-time |
| Enterprise platform | Large organization | Production control plane, standard support and core connectors | $150k-$450k ARR |
| Sovereign platform | Government, critical infrastructure, regulated group | Air gap, HSM, residency, Arabic operations, DR and premium support | $750k-$3m ARR plus implementation |
| Managed TrustOps | Organization transferring daily operations | Platform plus policy, privileged-access and evidence operations | Base platform plus $20k-$100k monthly |
| OEM and integrator edition | MSSP, system integrator, robotics or security vendor | White label, tenant administration, certification and partner enablement | $250k-$1m annual minimum plus usage |
| Independent assurance | Board, insurer, procurement or regulator | Scoped evidence review and signed report | $30k-$150k per assessment |

## Metering model

Do not charge solely per employee. The system governs non-human identities and high-consequence decisions.

```text
Annual contract value = platform minimum
                      + governed identity bands
                      + privileged target bands
                      + protected action volume
                      + evidence retention tier
                      + regulated deployment premium
                      + support and managed-service scope
```

Recommended billable meters:

- active governed human and non-human identities;
- active privileged targets and protected applications;
- policy decisions or protected actions per month;
- evidence volume and retention period;
- production regions, isolated environments and air-gapped sites;
- premium connectors and assurance profiles.

Never meter denied security events in a way that discourages enforcement.

## Unit-economic targets

These are operating targets, not current performance claims.

| Metric | Pilot target | Scaled target |
|---|---:|---:|
| Software gross margin | 60%-70% | 80%-88% |
| Managed-service gross margin | 35%-50% | 55%-65% |
| Implementation contribution margin | 20%-35% | 35%-45% with repeatable adapters |
| Annual gross retention | N/A | More than 90% |
| Net revenue retention | N/A | 115%-130% |
| CAC payback | Founder-led | Less than 18 months |
| Support hours per 1,000 governed identities per month | Establish baseline | Less than 8 hours excluding incidents |
| Standard connector deployment | 2-4 weeks | Less than 5 business days |

Customer contribution margin must be calculated from observed delivery data:

```text
Contribution margin = contract revenue
                    - cloud and storage
                    - third-party licenses
                    - support labor
                    - managed operations labor
                    - customer-specific connector maintenance
                    - assurance and hosting costs
```

## Defensible commercial moat

1. **Conformance gravity:** vendors implement the public receipt and adapter contracts.
2. **Integration depth:** supported identity, PAM, cloud, OT, biometric and robotics connectors.
3. **Evidence network:** reusable GRC Claw assurance envelopes accepted by buyers and auditors.
4. **Operational corpus:** redacted failure modes, policy tests, deployment telemetry and benchmark history.
5. **Sovereign delivery:** Arabic operation, air-gapped deployment, local residency and regional support.
6. **Certification mark:** independently governed compatibility and operating-effectiveness programs.
7. **Partner economics:** integrators can earn implementation revenue without forking the control standard.

The moat must come from execution and trusted network effects. A concealed universal credential would create a catastrophic liability and destroy international procurement credibility.

## Corporate and stewardship structure

A practical structure to evaluate with Egyptian and international counsel:

- an operating company owns commercial software, customer contracts and service delivery;
- a separate stewardship entity controls the open specification, neutral conformance rules and marks under a published charter;
- the founder retains economic control through equity, board rights, trademarks licensed on defined terms and reserved corporate matters;
- cryptographic production authority is held through audited quorum custody rather than a personal permanent key;
- an independent security council can suspend compromised releases or certification, but cannot appropriate the company or operate customer environments;
- succession documents define who can exercise corporate, specification, signing and recovery powers under incapacity or death.

Legal entities, share classes, trusts and cross-border ownership must be designed for the actual jurisdictions and tax residence. The repository should document the operating model without presenting it as a legal implementation.

