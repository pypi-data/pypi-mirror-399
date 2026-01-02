"""
Reminix SDK Core

Backward compatibility module providing access to core Reminix SDK functionality.
"""

from reminix.client import (
    APIError,
    AuthenticationError,
    Client,
    ClientConfig,
    NetworkError,
    ReminixError,
    PaginatedResponse,
    collect_all,
    paginate_all,
)

__all__ = [
    "Client",
    "ClientConfig",
    "ReminixError",
    "APIError",
    "AuthenticationError",
    "NetworkError",
    "PaginatedResponse",
    "paginate_all",
    "collect_all",
]
