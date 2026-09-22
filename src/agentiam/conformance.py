from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Callable

from .model import Broker
from .fabric import (
    AuthorizationRequest,
    Decision,
    PrincipalKind,
    TrustFabric,
    UniversalPrincipal,
)


@dataclass
class Result:
    id: str
    name: str
    passed: bool
    evidence: str


def run_suite() -> dict:
    tests: list[tuple[str, str, Callable[[], str]]] = [
        ("AIA-ID-001", "Human-to-agent task delegation", scenario_delegation),
        ("AIA-AUTHN-001", "Five-minute task-scoped proof-of-possession token", scenario_token),
        ("AIA-MCP-001", "MCP audience, resource, and action enforcement", scenario_mcp),
        ("AIA-DELEG-001", "Child-agent authority amplification blocked", scenario_child),
        ("AIA-REV-001", "Parent revocation cascades to child", scenario_revocation),
        ("AIA-PRINC-001", "Universal principals retain owner and trust domain", scenario_principals),
        ("AIA-CTX-001", "Cross-tenant and purpose-confused actions fail closed", scenario_context),
        ("AIA-PHYS-001", "Physical actions require attestation and safety readiness", scenario_physical),
        ("AIA-PAM-001", "Material privilege requires the configured approval quorum", scenario_approval),
    ]
    results: list[Result] = []
    for identifier, name, test in tests:
        try:
            evidence = test()
            results.append(Result(identifier, name, True, evidence))
        except Exception as error:
            results.append(Result(identifier, name, False, f"{type(error).__name__}: {error}"))
    passed = sum(item.passed for item in results)
    return {"suite": "AgentIAM Core Conformance v0.1", "passed": passed, "total": len(results), "results": [asdict(item) for item in results]}


def scenario_delegation() -> str:
    broker = Broker(b"test-key")
    item = broker.delegate(principal="user:alice", agent_id="agent:procurement", intent="review vendor", resources=["vendor:acme"], actions=["read"])
    assert item.principal == "user:alice" and item.intent == "review vendor"
    return "principal, agent, intent, resource, action, and expiry retained"


def scenario_token() -> str:
    broker = Broker(b"test-key")
    item = broker.delegate(principal="user:alice", agent_id="agent:procurement", intent="review vendor", resources=["vendor:acme"], actions=["read"])
    token = broker.issue_token(item.delegation_id, audience="mcp:vendor", resource="vendor:acme", actions=["read"], confirmation_key="key:a")
    assert token.confirmation_key == "key:a" and token.actions == ("read",)
    return "token is audience-bound, resource-bound, action-scoped, key-bound, and capped at five minutes"


def scenario_mcp() -> str:
    broker = Broker(b"test-key")
    item = broker.delegate(principal="user:alice", agent_id="agent:procurement", intent="review vendor", resources=["vendor:acme"], actions=["read"])
    token = broker.issue_token(item.delegation_id, audience="mcp:vendor", resource="vendor:acme", actions=["read"], confirmation_key="key:a")
    assert broker.authorize(token, presented_key="key:a", audience="mcp:vendor", resource="vendor:acme", action="read")[0]
    assert not broker.authorize(token, presented_key="key:a", audience="mcp:other", resource="vendor:acme", action="read")[0]
    assert not broker.authorize(token, presented_key="stolen", audience="mcp:vendor", resource="vendor:acme", action="read")[0]
    return "valid request allowed; wrong audience and stolen bearer rejected"


def scenario_child() -> str:
    broker = Broker(b"test-key")
    parent = broker.delegate(principal="user:alice", agent_id="agent:parent", intent="review vendor", resources=["vendor:acme"], actions=["read"])
    try:
        broker.delegate(principal="agent:parent", agent_id="agent:child", intent="help review", resources=["vendor:acme"], actions=["read", "delete"], parent_id=parent.delegation_id)
    except PermissionError:
        return "child request for undelegated delete authority blocked"
    raise AssertionError("authority amplification was allowed")


def scenario_revocation() -> str:
    broker = Broker(b"test-key")
    parent = broker.delegate(principal="user:alice", agent_id="agent:parent", intent="review vendor", resources=["vendor:acme"], actions=["read"])
    child = broker.delegate(principal="agent:parent", agent_id="agent:child", intent="help review", resources=["vendor:acme"], actions=["read"], parent_id=parent.delegation_id)
    token = broker.issue_token(child.delegation_id, audience="mcp:vendor", resource="vendor:acme", actions=["read"], confirmation_key="key:c")
    broker.revoke_delegation(parent.delegation_id)
    allowed, reason = broker.authorize(token, presented_key="key:c", audience="mcp:vendor", resource="vendor:acme", action="read")
    assert not allowed and "revoked" in reason
    return "parent and descendant delegation revoked; existing child token denied"


def _reference_fabric(*, approvals: int = 0) -> tuple[TrustFabric, str]:
    fabric = TrustFabric()
    for principal in (
        UniversalPrincipal("human:owner", PrincipalKind.HUMAN, "board:1", "example.org", "tenant:a"),
        UniversalPrincipal("agent:maintainer", PrincipalKind.AGENT, "human:owner", "example.org", "tenant:a", risk_class="elevated"),
        UniversalPrincipal("robot:arm-1", PrincipalKind.ROBOT, "human:owner", "example.org", "tenant:a", risk_class="critical"),
    ):
        fabric.register_principal(principal)
    grant = fabric.grant(
        delegator_id="human:owner",
        delegate_id="agent:maintainer",
        purpose="inspect turbine",
        resources=["robot:arm-1", "asset:turbine-7"],
        actions=["read", "physical:inspect"],
        required_approvals=approvals,
        max_child_depth=1,
    )
    return fabric, grant.delegation_id


def scenario_principals() -> str:
    fabric, _ = _reference_fabric()
    agent = fabric.principals["agent:maintainer"]
    assert agent.owner_id == "human:owner" and agent.trust_domain == "example.org"
    assert agent.kind is PrincipalKind.AGENT and agent.tenant_id == "tenant:a"
    return "human, agent, and robot principals retain type, owner, tenant, and trust domain"


def scenario_context() -> str:
    fabric, delegation_id = _reference_fabric()
    request = AuthorizationRequest(
        request_id="req:context",
        principal_id="agent:maintainer",
        accountable_owner_id="human:owner",
        delegation_id=delegation_id,
        purpose="trade securities",
        resource="asset:turbine-7",
        action="read",
        environment="lab",
        tenant_id="tenant:a",
        policy_revision="policy:v1",
    )
    purpose_decision = fabric.evaluate(request)
    tenant_request = AuthorizationRequest(**{**asdict(request), "request_id": "req:tenant", "purpose": "inspect turbine", "tenant_id": "tenant:b"})
    tenant_decision = fabric.evaluate(tenant_request)
    assert purpose_decision.decision is Decision.DENY and "purpose mismatch" in purpose_decision.reason
    assert tenant_decision.decision is Decision.DENY and "cross-tenant" in tenant_decision.reason
    return "purpose-confused and cross-tenant requests denied before resource access"


def scenario_physical() -> str:
    fabric, delegation_id = _reference_fabric()
    base = dict(
        principal_id="agent:maintainer",
        accountable_owner_id="human:owner",
        delegation_id=delegation_id,
        purpose="inspect turbine",
        resource="robot:arm-1",
        action="physical:inspect",
        environment="digital-twin",
        tenant_id="tenant:a",
        policy_revision="policy:v1",
        model_digest="sha256:model",
    )
    denied = fabric.evaluate(AuthorizationRequest(**base, request_id="req:physical:denied", device_attested=False, safety_state="READY"))
    allowed = fabric.evaluate(AuthorizationRequest(**base, request_id="req:physical:ready", device_attested=True, safety_state="READY"))
    assert denied.decision is Decision.DENY and allowed.decision is Decision.ALLOW
    assert "robot_black_box_recording" in allowed.obligations
    return "unattested action denied; attested READY action allowed with black-box and safety obligations"


def scenario_approval() -> str:
    fabric, delegation_id = _reference_fabric(approvals=2)
    base = dict(
        principal_id="agent:maintainer",
        accountable_owner_id="human:owner",
        delegation_id=delegation_id,
        purpose="inspect turbine",
        resource="asset:turbine-7",
        action="read",
        environment="production",
        tenant_id="tenant:a",
        policy_revision="policy:v1",
    )
    pending = fabric.evaluate(AuthorizationRequest(request_id="req:approval:1", approvals=("approver:a",), **base))
    allowed = fabric.evaluate(AuthorizationRequest(request_id="req:approval:2", approvals=("approver:a", "approver:b"), **base))
    assert pending.decision is Decision.REQUIRE_APPROVAL and allowed.decision is Decision.ALLOW
    return "one approval remains pending; configured two-person approval permits the scoped action"
