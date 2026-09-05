"""Intentionally vulnerable teaching fixture. Never deploy this code."""


def authorize(shared_api_key: str, supplied_api_key: str, _resource: str, _action: str) -> bool:
    """Demonstrates the anti-pattern: a bearer secret grants every action on every resource."""
    return shared_api_key == supplied_api_key
