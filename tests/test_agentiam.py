import unittest

from agentiam.conformance import run_suite
from agentiam.model import Broker
from agentiam.fabric import (
    AuthorizationRequest,
    Decision,
    PrincipalKind,
    TrustFabric,
    UniversalPrincipal,
)


class AgentIAMTests(unittest.TestCase):
    def setUp(self):
        self.broker = Broker(b"deterministic-test-integrity-key")
        self.delegation = self.broker.delegate(
            principal="user:owner", agent_id="agent:worker", intent="read one record",
            resources=["record:1"], actions=["read"],
        )

    def test_conformance_suite(self):
        report = run_suite()
        self.assertEqual(report["passed"], 9)
        self.assertEqual(report["total"], 9)

    def test_scope_escalation_denied(self):
        with self.assertRaises(PermissionError):
            self.broker.issue_token(self.delegation.delegation_id, audience="mcp:data", resource="record:1", actions=["delete"], confirmation_key="key:1")

    def test_wrong_audience_denied(self):
        token = self.broker.issue_token(self.delegation.delegation_id, audience="mcp:data", resource="record:1", actions=["read"], confirmation_key="key:1")
        allowed, reason = self.broker.authorize(token, presented_key="key:1", audience="mcp:other", resource="record:1", action="read")
        self.assertFalse(allowed)
        self.assertEqual(reason, "audience mismatch")

    def test_stolen_bearer_denied(self):
        token = self.broker.issue_token(self.delegation.delegation_id, audience="mcp:data", resource="record:1", actions=["read"], confirmation_key="key:1")
        allowed, reason = self.broker.authorize(token, presented_key="stolen", audience="mcp:data", resource="record:1", action="read")
        self.assertFalse(allowed)
        self.assertEqual(reason, "proof-of-possession failed")

    def test_receipt_integrity(self):
        token = self.broker.issue_token(self.delegation.delegation_id, audience="mcp:data", resource="record:1", actions=["read"], confirmation_key="key:1")
        receipt = self.broker.receipt(token=token, intent="read one record", resource="record:1", action="read", decision="ALLOW", result={"status": "ok"})
        self.assertTrue(self.broker.verify_receipt(receipt))
        receipt["action"] = "delete"
        self.assertFalse(self.broker.verify_receipt(receipt))
        self.assertFalse(receipt["integrity"]["non_repudiation"])

    def test_revocation_denies_existing_token(self):
        token = self.broker.issue_token(self.delegation.delegation_id, audience="mcp:data", resource="record:1", actions=["read"], confirmation_key="key:1")
        self.broker.revoke_delegation(self.delegation.delegation_id)
        self.assertFalse(self.broker.authorize(token, presented_key="key:1", audience="mcp:data", resource="record:1", action="read")[0])


class TrustFabricTests(unittest.TestCase):
    def setUp(self):
        self.fabric = TrustFabric()
        self.fabric.register_principal(UniversalPrincipal("human:owner", PrincipalKind.HUMAN, "board:1", "example.org", "tenant:a"))
        self.fabric.register_principal(UniversalPrincipal("agent:operator", PrincipalKind.AGENT, "human:owner", "example.org", "tenant:a"))
        self.fabric.register_principal(UniversalPrincipal("robot:arm", PrincipalKind.ROBOT, "human:owner", "example.org", "tenant:a", risk_class="critical"))
        self.grant = self.fabric.grant(
            delegator_id="human:owner",
            delegate_id="agent:operator",
            purpose="inspect turbine",
            resources=["robot:arm", "asset:turbine"],
            actions=["read", "physical:inspect"],
            max_child_depth=1,
        )

    def request(self, **overrides):
        values = {
            "request_id": "req:1",
            "principal_id": "agent:operator",
            "accountable_owner_id": "human:owner",
            "delegation_id": self.grant.delegation_id,
            "purpose": "inspect turbine",
            "resource": "asset:turbine",
            "action": "read",
            "environment": "lab",
            "tenant_id": "tenant:a",
            "policy_revision": "policy:v1",
        }
        values.update(overrides)
        return AuthorizationRequest(**values)

    def test_purpose_and_tenant_are_enforced(self):
        self.assertEqual(self.fabric.evaluate(self.request(purpose="trade securities")).decision, Decision.DENY)
        self.assertEqual(self.fabric.evaluate(self.request(tenant_id="tenant:b")).decision, Decision.DENY)

    def test_physical_lease_is_short_lived_and_evidence_bound(self):
        request = self.request(
            request_id="req:physical",
            resource="robot:arm",
            action="physical:inspect",
            device_attested=True,
            safety_state="READY",
            model_digest="sha256:model-v1",
        )
        decision = self.fabric.evaluate(request)
        self.assertEqual(decision.decision, Decision.ALLOW)
        lease = self.fabric.issue_physical_lease(request, decision, robot_id="robot:arm", operating_domain="cell:a", ttl_seconds=120)
        self.assertEqual(lease.decision_id, decision.decision_id)
        self.assertEqual(len(lease.evidence_digest), 64)
        from datetime import datetime
        issued = datetime.fromisoformat(lease.issued_at.replace("Z", "+00:00"))
        expires = datetime.fromisoformat(lease.expires_at.replace("Z", "+00:00"))
        self.assertLessEqual((expires - issued).total_seconds(), 30)

        substituted = self.request(
            request_id="req:physical:substituted",
            resource="robot:arm",
            action="physical:inspect",
            device_attested=True,
            safety_state="READY",
            model_digest="sha256:model-v1",
        )
        with self.assertRaises(PermissionError):
            self.fabric.issue_physical_lease(substituted, decision, robot_id="robot:arm", operating_domain="cell:a")

    def test_parent_revocation_invalidates_descendant(self):
        self.fabric.register_principal(UniversalPrincipal("agent:child", PrincipalKind.AGENT, "human:owner", "example.org", "tenant:a"))
        child = self.fabric.grant(
            delegator_id="agent:operator",
            delegate_id="agent:child",
            purpose="inspect turbine",
            resources=["asset:turbine"],
            actions=["read"],
            parent_id=self.grant.delegation_id,
        )
        self.fabric.revoke(self.grant.delegation_id)
        child_request = self.request(principal_id="agent:child", delegation_id=child.delegation_id)
        self.assertEqual(self.fabric.evaluate(child_request).decision, Decision.DENY)


if __name__ == "__main__":
    unittest.main()
