"""
Reminix Python SDK

Official Python SDK for the Reminix platform.
Includes API client, adapters, runtime, integrations, and tools for building AI applications.
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

__version__ = "0.5.0"

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
    "__version__",
]
