"""Reference use of the AgentIAM broker."""

from agentiam.model import Broker


def demonstration() -> tuple[bool, str]:
    broker = Broker()
    delegation = broker.delegate(
        principal="user:procurement-owner", agent_id="agent:vendor-review",
        intent="read one vendor record", resources=["vendor:acme"], actions=["read"],
    )
    token = broker.issue_token(
        delegation.delegation_id, audience="mcp:vendor-records",
        resource="vendor:acme", actions=["read"], confirmation_key="ephemeral-public-key-thumbprint",
    )
    return broker.authorize(
        token, presented_key="ephemeral-public-key-thumbprint",
        audience="mcp:vendor-records", resource="vendor:acme", action="read",
    )
