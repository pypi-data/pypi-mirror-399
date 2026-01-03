"""
Sharesight Python SDK
A professional Python interface for the Sharesight API (v2 and v3).
"""

__version__ = "0.1.0"

from .client import SharesightClient
from .auth import TokenStore, FileTokenStore
from .exceptions import (
    SharesightError,
    SharesightAuthError,
    SharesightAPIError,
    SharesightRateLimitError
)

__all__ = [
    "SharesightClient",
    "TokenStore",
    "FileTokenStore",
    "SharesightError",
    "SharesightAuthError",
    "SharesightAPIError",
    "SharesightRateLimitError"
]
