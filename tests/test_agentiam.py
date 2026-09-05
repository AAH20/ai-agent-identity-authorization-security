import unittest

from agentiam.conformance import run_suite
from agentiam.model import Broker


class AgentIAMTests(unittest.TestCase):
    def setUp(self):
        self.broker = Broker(b"deterministic-test-integrity-key")
        self.delegation = self.broker.delegate(
            principal="user:owner", agent_id="agent:worker", intent="read one record",
            resources=["record:1"], actions=["read"],
        )

    def test_conformance_suite(self):
        report = run_suite()
        self.assertEqual(report["passed"], 5)
        self.assertEqual(report["total"], 5)

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


if __name__ == "__main__":
    unittest.main()
