"""
Custom exceptions for the Sharesight SDK.
"""

class SharesightError(Exception):
    """Base exception for all Sharesight SDK errors."""
    pass

class SharesightAuthError(SharesightError):
    """Raised when authentication fails."""
    pass

class SharesightAPIError(SharesightError):
    """Raised when the API returns an error response."""
    def __init__(self, message, status_code=None, response_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

class SharesightRateLimitError(SharesightAPIError):
    """Raised when the API rate limit is exceeded."""
    pass
