from __future__ import annotations

import hashlib
import hmac
import json
import secrets
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


@dataclass(frozen=True)
class Delegation:
    delegation_id: str
    principal: str
    agent_id: str
    intent: str
    resources: tuple[str, ...]
    actions: tuple[str, ...]
    issued_at: str
    expires_at: str
    parent_id: str | None = None
    revoked: bool = False


@dataclass(frozen=True)
class TaskToken:
    token_id: str
    agent_id: str
    delegation_id: str
    audience: str
    resource: str
    actions: tuple[str, ...]
    issued_at: str
    expires_at: str
    confirmation_key: str


class Broker:
    """Deterministic reference broker. It models controls, not production cryptography."""

    def __init__(self, integrity_key: bytes | None = None):
        self.integrity_key = integrity_key or secrets.token_bytes(32)
        self.delegations: dict[str, Delegation] = {}
        self.revoked_tokens: set[str] = set()

    def delegate(self, *, principal: str, agent_id: str, intent: str, resources: list[str], actions: list[str], ttl_seconds: int = 300, parent_id: str | None = None) -> Delegation:
        if ttl_seconds <= 0 or ttl_seconds > 3600:
            raise ValueError("delegation TTL must be between 1 and 3600 seconds")
        if not principal or not agent_id or not intent or not resources or not actions:
            raise ValueError("delegation requires principal, agent, intent, resources, and actions")
        if parent_id:
            parent = self._active_delegation(parent_id)
            if not set(resources).issubset(parent.resources) or not set(actions).issubset(parent.actions):
                raise PermissionError("child delegation cannot amplify parent authority")
        issued = now()
        item = Delegation(
            delegation_id=f"dlg_{secrets.token_hex(8)}", principal=principal,
            agent_id=agent_id, intent=intent, resources=tuple(sorted(set(resources))),
            actions=tuple(sorted(set(actions))), issued_at=iso(issued),
            expires_at=iso(issued + timedelta(seconds=ttl_seconds)), parent_id=parent_id,
        )
        self.delegations[item.delegation_id] = item
        return item

    def issue_token(self, delegation_id: str, *, audience: str, resource: str, actions: list[str], confirmation_key: str, ttl_seconds: int = 300) -> TaskToken:
        delegation = self._active_delegation(delegation_id)
        if resource not in delegation.resources or not set(actions).issubset(delegation.actions):
            raise PermissionError("requested token exceeds delegated authority")
        if not audience or not confirmation_key:
            raise ValueError("audience and proof-of-possession key are required")
        issued = now()
        delegation_expiry = datetime.fromisoformat(delegation.expires_at.replace("Z", "+00:00"))
        expiry = min(issued + timedelta(seconds=max(1, min(ttl_seconds, 300))), delegation_expiry)
        return TaskToken(
            token_id=f"tok_{secrets.token_hex(8)}", agent_id=delegation.agent_id,
            delegation_id=delegation_id, audience=audience, resource=resource,
            actions=tuple(sorted(set(actions))), issued_at=iso(issued), expires_at=iso(expiry),
            confirmation_key=confirmation_key,
        )

    def authorize(self, token: TaskToken, *, presented_key: str, audience: str, resource: str, action: str) -> tuple[bool, str]:
        try:
            delegation = self._active_delegation(token.delegation_id)
        except (KeyError, PermissionError) as error:
            return False, str(error)
        expiry = datetime.fromisoformat(token.expires_at.replace("Z", "+00:00"))
        checks = (
            (token.token_id not in self.revoked_tokens, "token revoked"),
            (expiry >= now(), "token expired"),
            (hmac.compare_digest(token.confirmation_key, presented_key), "proof-of-possession failed"),
            (token.audience == audience, "audience mismatch"),
            (token.resource == resource, "resource mismatch"),
            (action in token.actions, "action outside token scope"),
            (resource in delegation.resources and action in delegation.actions, "authority no longer delegated"),
        )
        for passed, reason in checks:
            if not passed:
                return False, reason
        return True, "authorized"

    def revoke_delegation(self, delegation_id: str) -> None:
        item = self.delegations[delegation_id]
        self.delegations[delegation_id] = Delegation(**{**asdict(item), "revoked": True})
        for child_id, child in list(self.delegations.items()):
            if child.parent_id == delegation_id and not child.revoked:
                self.revoke_delegation(child_id)

    def receipt(self, *, token: TaskToken, intent: str, resource: str, action: str, decision: str, result: Any) -> dict[str, Any]:
        delegation = self.delegations[token.delegation_id]
        body = {
            "receipt_version": "1.0", "receipt_id": f"rcpt_{secrets.token_hex(8)}",
            "timestamp": iso(now()), "agent_id": token.agent_id,
            "human_or_service_principal": delegation.principal,
            "delegation_id": delegation.delegation_id, "parent_delegation_id": delegation.parent_id,
            "intent": intent, "audience": token.audience, "resource": resource,
            "action": action, "policy_decision": decision,
            "token_id_hash": hashlib.sha256(token.token_id.encode()).hexdigest(),
            "result_hash": hashlib.sha256(canonical(result)).hexdigest(),
        }
        return {
            **body,
            "integrity": {
                "method": "HMAC-SHA256-LAB-ONLY",
                "value": hmac.new(self.integrity_key, canonical(body), hashlib.sha256).hexdigest(),
                "non_repudiation": False,
                "warning": "Shared-secret integrity is not public-key non-repudiation",
            },
        }

    def verify_receipt(self, receipt: dict[str, Any]) -> bool:
        integrity = receipt["integrity"]
        body = {key: value for key, value in receipt.items() if key != "integrity"}
        expected = hmac.new(self.integrity_key, canonical(body), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, integrity["value"])

    def _active_delegation(self, delegation_id: str) -> Delegation:
        item = self.delegations[delegation_id]
        if item.revoked:
            raise PermissionError("delegation revoked")
        if datetime.fromisoformat(item.expires_at.replace("Z", "+00:00")) < now():
            raise PermissionError("delegation expired")
        if item.parent_id:
            self._active_delegation(item.parent_id)
        return item
