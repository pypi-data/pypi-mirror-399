"""
Agimus Python SDK.

A Python client for the Agimus Platform Object Store API.

Usage:
    from agimus import AgimusClient

    client = AgimusClient(api_key="agm_...")

    # Query objects
    customers = client.objects("customer").filter(status="active").all()

    # Get single object
    customer = client.objects("customer").get("C123")

    # Create
    new_customer = client.objects("customer").create({"id": "C999", "name": "Acme"})

    # Update
    updated = client.objects("customer").update("C123", {"status": "premium"})

    # Delete
    client.objects("customer").delete("C123")
"""
from .client import AgimusClient
from .exceptions import (
    AgimusError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    AccessDeniedError,
    RateLimitError,
    ServerError,
    APIError,
)

__version__ = "0.1.0"

__all__ = [
    "AgimusClient",
    "AgimusError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "AccessDeniedError",
    "RateLimitError",
    "ServerError",
    "APIError",
]
