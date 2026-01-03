"""
LTFI-WSAP Python SDK

Official Python SDK for the Layered Transformer Framework Intelligence - Web System Alignment Protocol
"""

__version__ = "2.0.2"

from .client import Client
from .models import (
    Entity,
    Domain,
    Verification,
    WSAPData,
    CreateEntityRequest,
    UpdateEntityRequest,
    DisclosureLevel,
    VerificationStatus,
)
from .exceptions import (
    WSAPException,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NotFoundError,
)

__all__ = [
    "Client",
    "Entity",
    "Domain",
    "Verification",
    "WSAPData",
    "CreateEntityRequest",
    "UpdateEntityRequest",
    "DisclosureLevel",
    "VerificationStatus",
    "WSAPException",
    "AuthenticationError",
    "ValidationError",
    "RateLimitError",
    "NotFoundError",
]