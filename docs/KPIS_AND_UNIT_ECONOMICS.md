# AgentIAM KPIs and Unit Economics

## Identity security

| KPI | Formula | Target |
|---|---|---:|
| Distinct identity coverage | agents with unique identities / active agents | 100% |
| Shared static credential rate | agents using shared long-lived secrets / active agents | 0% |
| Identity-owner coverage | agents with accountable owners / active agents | 100% |
| Orphaned-agent rate | active agents without current purpose or owner / active agents | 0% |
| Short-lived credential coverage | tasks using credentials inside approved TTL / tasks | 100% |
| Replay success | accepted replay attempts / replay attempts | 0% |
| Revocation enforcement | denied post-revocation attempts / attempts | 100% |
| Revocation propagation | median and p95 revoke-to-deny time | Lower |

## Authorization and delegation

| KPI | Formula | Target |
|---|---|---:|
| Default-deny enforcement | denied unspecified actions / unspecified attempts | 100% |
| Excess-permission rate | unused or unjustified grants / grants | 0% |
| Unauthorized action rate | unauthorized successful actions / attempted actions | 0% |
| Approval enforcement | blocked unapproved material actions / attempts | 100% |
| Authority amplification | child grants exceeding parent / child grants | 0% |
| Cross-tenant access | protected records reached across tenants | 0 |
| Delegation-chain coverage | actions with complete lineage / actions | 100% |
| Action reconstruction | receipts that reconstruct principal, intent, policy and result / receipts | 100% |
| False-allow rate | invalid requests allowed / invalid requests | 0% |
| False-denial rate | valid requests denied / valid requests | Minimize |

## Operational performance

- Agent onboarding time
- Policy authoring and review time
- Mean time to understand agent intent
- Authorization latency p50, p95 and p99
- Credentials issued per completed task
- Approval waiting time
- Revocation recovery time
- Policy changes per month
- Incidents per 10,000 authorized tasks
- Monthly policy-maintenance hours

## Customer unit economics

```text
Annual Agent IAM cost = identity infrastructure + policy engineering
                      + credential issuance + authorization compute
                      + approval labor + monitoring
                      + incident and exception handling

Cost per governed agent = annual Agent IAM cost / active governed agents

Cost per authorized task = issuance + evaluation + approval
                         + receipt storage + exception handling

Avoided credential cost = retired static credentials
                        × annual rotation, review and incident cost

Agent onboarding value = agents onboarded
                       × (baseline hours - controlled onboarding hours)
                       × loaded engineering cost

Expected-loss reduction = baseline identity-related expected loss
                        - residual expected loss after controls

ROI = (onboarding value + avoided credential cost
     + avoided approval rework + expected-loss reduction
     + Finance-validated attributed contribution margin
     - annual Agent IAM cost) / annual Agent IAM cost
```

## Revenue enablement

```text
Attributed contribution margin = eligible contract value
                               × realization probability after a verified IAM gate closes
                               × AgentIAM attribution
                               × contribution margin
```

The opportunity must name the customer, assurance requirement, blocked identity or authorization gate, closure timestamp, activation window, revenue owner and Finance approver. Report influenced pipeline separately and never add it to ROI.

## Provider economics

Track compute per authorization decision, receipt-storage cost, support hours per 100 agents, adapter-maintenance cost, gross margin per tenant, expansion revenue per additional agent, gross retention and acquisition payback.

Publish conservative, base and upside scenarios. State volumes, loaded rates, incident probabilities and attribution. A model without disclosed inputs is not decision-grade.
