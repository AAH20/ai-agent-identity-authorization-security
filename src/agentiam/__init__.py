"""AgentIAM Lab: AI agent identity and authorization conformance."""

__version__ = "0.1.0"
from .fabric import (
    AuthorizationDecision,
    AuthorizationRequest,
    Decision,
    DelegationGrant,
    PhysicalActionLease,
    PrincipalKind,
    TrustFabric,
    UniversalPrincipal,
)

__all__ = [
    "AuthorizationDecision",
    "AuthorizationRequest",
    "Decision",
    "DelegationGrant",
    "PhysicalActionLease",
    "PrincipalKind",
    "TrustFabric",
    "UniversalPrincipal",
]
