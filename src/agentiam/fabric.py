from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


class PrincipalKind(str, Enum):
    HUMAN = "human"
    SERVICE = "service"
    WORKLOAD = "workload"
    AGENT = "agent"
    MODEL = "model"
    TOOL = "tool"
    DEVICE = "device"
    ROBOT = "robot"
    VEHICLE = "vehicle"
    BIOMETRIC_ASSERTION = "biometric_assertion"
    DATA_PRODUCT = "data_product"


class Decision(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"


@dataclass(frozen=True)
class UniversalPrincipal:
    principal_id: str
    kind: PrincipalKind
    owner_id: str
    trust_domain: str
    tenant_id: str
    risk_class: str = "standard"
    jurisdiction: str = "unspecified"
    active: bool = True
    attributes: dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if not all((self.principal_id, self.owner_id, self.trust_domain, self.tenant_id)):
            raise ValueError("principal requires identity, owner, trust domain, and tenant")
        if not isinstance(self.kind, PrincipalKind):
            raise ValueError("principal kind must be a supported PrincipalKind")
        if self.risk_class not in {"standard", "elevated", "critical"}:
            raise ValueError("unsupported principal risk class")


@dataclass(frozen=True)
class DelegationGrant:
    delegation_id: str
    delegator_id: str
    delegate_id: str
    purpose: str
    resources: tuple[str, ...]
    actions: tuple[str, ...]
    issued_at: str
    expires_at: str
    parent_id: str | None = None
    max_child_depth: int = 0
    remaining_budget: float | None = None
    geographic_boundary: tuple[str, ...] = ()
    data_classifications: tuple[str, ...] = ("public",)
    required_approvals: int = 0
    revoked: bool = False


@dataclass(frozen=True)
class AuthorizationRequest:
    request_id: str
    principal_id: str
    accountable_owner_id: str
    delegation_id: str
    purpose: str
    resource: str
    action: str
    environment: str
    tenant_id: str
    policy_revision: str
    risk_score: float = 0.0
    approvals: tuple[str, ...] = ()
    device_attested: bool = False
    safety_state: str | None = None
    model_digest: str | None = None
    context_refs: tuple[str, ...] = ()


@dataclass(frozen=True)
class AuthorizationDecision:
    decision_id: str
    request_id: str
    decision: Decision
    reason: str
    policy_revision: str
    decided_at: str
    expires_at: str
    obligations: tuple[str, ...]
    evidence_digest: str


@dataclass(frozen=True)
class PhysicalActionLease:
    lease_id: str
    principal_id: str
    robot_id: str
    delegation_id: str
    action: str
    operating_domain: str
    model_digest: str
    policy_revision: str
    issued_at: str
    expires_at: str
    decision_id: str
    evidence_digest: str


class TrustFabric:
    """Reference decision plane for conformance tests, not a production IAM/PAM service."""

    def __init__(self) -> None:
        self.principals: dict[str, UniversalPrincipal] = {}
        self.delegations: dict[str, DelegationGrant] = {}

    def register_principal(self, principal: UniversalPrincipal) -> None:
        principal.validate()
        if principal.principal_id in self.principals:
            raise ValueError("principal already registered")
        self.principals[principal.principal_id] = principal

    def grant(
        self,
        *,
        delegator_id: str,
        delegate_id: str,
        purpose: str,
        resources: list[str],
        actions: list[str],
        ttl_seconds: int = 300,
        parent_id: str | None = None,
        max_child_depth: int = 0,
        required_approvals: int = 0,
        remaining_budget: float | None = None,
        geographic_boundary: list[str] | None = None,
        data_classifications: list[str] | None = None,
    ) -> DelegationGrant:
        delegator = self._principal(delegator_id)
        delegate = self._principal(delegate_id)
        if delegator.tenant_id != delegate.tenant_id:
            raise PermissionError("cross-tenant delegation denied")
        if ttl_seconds < 1 or ttl_seconds > 3600:
            raise ValueError("delegation TTL must be between 1 and 3600 seconds")
        if not purpose or not resources or not actions:
            raise ValueError("delegation requires purpose, resources, and actions")
        if max_child_depth < 0:
            raise ValueError("max child depth cannot be negative")

        if parent_id:
            parent = self._active_grant(parent_id)
            if parent.delegate_id != delegator_id:
                raise PermissionError("only the parent delegate may create its child grant")
            if parent.max_child_depth < 1:
                raise PermissionError("parent delegation does not permit subdelegation")
            if not set(resources).issubset(parent.resources) or not set(actions).issubset(parent.actions):
                raise PermissionError("child delegation cannot amplify parent authority")
            if purpose != parent.purpose:
                raise PermissionError("child delegation cannot change the authorized purpose")
            max_child_depth = min(max_child_depth, parent.max_child_depth - 1)
            required_approvals = max(required_approvals, parent.required_approvals)
            if parent.remaining_budget is not None:
                if remaining_budget is None or remaining_budget > parent.remaining_budget:
                    raise PermissionError("child delegation cannot amplify parent budget")

        issued = _utc_now()
        grant = DelegationGrant(
            delegation_id=f"dlg_{secrets.token_hex(8)}",
            delegator_id=delegator_id,
            delegate_id=delegate_id,
            purpose=purpose,
            resources=tuple(sorted(set(resources))),
            actions=tuple(sorted(set(actions))),
            issued_at=_iso(issued),
            expires_at=_iso(issued + timedelta(seconds=ttl_seconds)),
            parent_id=parent_id,
            max_child_depth=max_child_depth,
            remaining_budget=remaining_budget,
            geographic_boundary=tuple(sorted(set(geographic_boundary or []))),
            data_classifications=tuple(sorted(set(data_classifications or ["public"]))),
            required_approvals=required_approvals,
        )
        self.delegations[grant.delegation_id] = grant
        return grant

    def evaluate(self, request: AuthorizationRequest, ttl_seconds: int = 30) -> AuthorizationDecision:
        reasons: list[str] = []
        obligations: list[str] = ["record_decision", "record_outcome"]
        decision = Decision.ALLOW

        try:
            principal = self._principal(request.principal_id)
            grant = self._active_grant(request.delegation_id)
        except (KeyError, PermissionError) as error:
            return self._decision(request, Decision.DENY, str(error), obligations, ttl_seconds)

        checks = (
            (grant.delegate_id == request.principal_id, "delegation is not assigned to this principal"),
            (principal.owner_id == request.accountable_owner_id, "accountable owner mismatch"),
            (principal.tenant_id == request.tenant_id, "cross-tenant request denied"),
            (grant.purpose == request.purpose, "purpose mismatch"),
            (request.resource in grant.resources, "resource outside delegated scope"),
            (request.action in grant.actions, "action outside delegated scope"),
            (0.0 <= request.risk_score <= 1.0, "risk score outside valid range"),
        )
        for passed, reason in checks:
            if not passed:
                reasons.append(reason)

        if reasons:
            decision = Decision.DENY
        elif request.risk_score >= 0.90:
            decision, reasons = Decision.DENY, ["risk exceeds maximum tolerance"]
        elif len(request.approvals) < grant.required_approvals or request.risk_score >= 0.70:
            decision, reasons = Decision.REQUIRE_APPROVAL, ["additional approval required"]
            obligations.append("obtain_independent_approval")
        else:
            reasons = ["authorized within delegated purpose and scope"]

        if principal.kind in {PrincipalKind.ROBOT, PrincipalKind.VEHICLE} or request.action.startswith("physical:"):
            obligations.extend(("robot_black_box_recording", "independent_safety_controller"))
            if not request.device_attested or request.safety_state != "READY" or not request.model_digest:
                decision = Decision.DENY
                reasons = ["physical action requires attested device, READY safety state, and model digest"]

        return self._decision(request, decision, "; ".join(reasons), obligations, ttl_seconds)

    def issue_physical_lease(
        self,
        request: AuthorizationRequest,
        decision: AuthorizationDecision,
        *,
        robot_id: str,
        operating_domain: str,
        ttl_seconds: int = 15,
    ) -> PhysicalActionLease:
        if decision.decision is not Decision.ALLOW:
            raise PermissionError("physical lease requires an ALLOW decision")
        if decision.request_id != request.request_id or decision.policy_revision != request.policy_revision:
            raise PermissionError("decision is not bound to this request and policy revision")
        decision_expiry = datetime.fromisoformat(decision.expires_at.replace("Z", "+00:00"))
        if decision_expiry < _utc_now():
            raise PermissionError("authorization decision expired")
        if request.safety_state != "READY" or not request.device_attested or not request.model_digest:
            raise PermissionError("physical lease prerequisites are not satisfied")
        if not request.action.startswith("physical:") or request.resource != robot_id:
            raise PermissionError("physical lease action and robot must match the authorized request")
        required_obligations = {"robot_black_box_recording", "independent_safety_controller"}
        if not required_obligations.issubset(decision.obligations):
            raise PermissionError("physical lease decision is missing mandatory safety obligations")
        issued = _utc_now()
        expiry = issued + timedelta(seconds=max(1, min(ttl_seconds, 30)))
        body = {
            "principal_id": request.principal_id,
            "robot_id": robot_id,
            "delegation_id": request.delegation_id,
            "action": request.action,
            "operating_domain": operating_domain,
            "model_digest": request.model_digest,
            "policy_revision": request.policy_revision,
            "decision_id": decision.decision_id,
            "issued_at": _iso(issued),
            "expires_at": _iso(expiry),
        }
        return PhysicalActionLease(
            lease_id=f"lease_{secrets.token_hex(8)}",
            evidence_digest=_digest(body),
            **body,
        )

    def revoke(self, delegation_id: str) -> None:
        grant = self.delegations[delegation_id]
        self.delegations[delegation_id] = DelegationGrant(**{**asdict(grant), "revoked": True})
        for child_id, child in list(self.delegations.items()):
            if child.parent_id == delegation_id and not child.revoked:
                self.revoke(child_id)

    def _principal(self, principal_id: str) -> UniversalPrincipal:
        principal = self.principals[principal_id]
        if not principal.active:
            raise PermissionError("principal inactive")
        return principal

    def _active_grant(self, delegation_id: str) -> DelegationGrant:
        grant = self.delegations[delegation_id]
        if grant.revoked:
            raise PermissionError("delegation revoked")
        if datetime.fromisoformat(grant.expires_at.replace("Z", "+00:00")) < _utc_now():
            raise PermissionError("delegation expired")
        if grant.parent_id:
            self._active_grant(grant.parent_id)
        return grant

    def _decision(
        self,
        request: AuthorizationRequest,
        decision: Decision,
        reason: str,
        obligations: list[str],
        ttl_seconds: int,
    ) -> AuthorizationDecision:
        decided = _utc_now()
        body = {
            "request": asdict(request),
            "decision": decision.value,
            "reason": reason,
            "policy_revision": request.policy_revision,
            "obligations": sorted(set(obligations)),
        }
        return AuthorizationDecision(
            decision_id=f"dec_{secrets.token_hex(8)}",
            request_id=request.request_id,
            decision=decision,
            reason=reason,
            policy_revision=request.policy_revision,
            decided_at=_iso(decided),
            expires_at=_iso(decided + timedelta(seconds=max(1, min(ttl_seconds, 300)))),
            obligations=tuple(sorted(set(obligations))),
            evidence_digest=_digest(body),
        )
