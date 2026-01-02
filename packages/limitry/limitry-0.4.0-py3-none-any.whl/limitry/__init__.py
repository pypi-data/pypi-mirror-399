"""
Limitry Python SDK

Official Python SDK for the Limitry platform.
Includes API client, integrations, and tools for building with Limitry.
"""

from limitry.client import (
    APIError,
    AuthenticationError,
    Client,
    ClientConfig,
    LimitryError,
    NetworkError,
    PaginatedResponse,
    collect_all,
    paginate_all,
)

__version__ = "0.4.0"

__all__ = [
    "Client",
    "ClientConfig",
    "LimitryError",
    "APIError",
    "AuthenticationError",
    "NetworkError",
    "PaginatedResponse",
    "paginate_all",
    "collect_all",
    "__version__",
]
