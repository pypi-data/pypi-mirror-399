"""
Limitry SDK Core

Backward compatibility module providing access to core Limitry SDK functionality.
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
]
