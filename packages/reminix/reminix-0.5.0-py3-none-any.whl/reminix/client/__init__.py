"""
Reminix API Client
"""

from .client import Client
from .config import ClientConfig
from .exceptions import (
    APIError,
    AuthenticationError,
    NetworkError,
    ReminixError,
)
from .utils.pagination import PaginatedResponse, collect_all, paginate_all

# fmt: off
# BEGIN AUTO-GENERATED RESOURCES EXPORT
from .resources import (
    Project,
)
# END AUTO-GENERATED RESOURCES EXPORT
# fmt: on

# fmt: off
# BEGIN AUTO-GENERATED __ALL__
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
    "Project",
]
# END AUTO-GENERATED __ALL__
# fmt: on
