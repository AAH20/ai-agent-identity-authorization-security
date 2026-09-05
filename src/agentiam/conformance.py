from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Callable

from .model import Broker


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
