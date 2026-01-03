"""
Custom exceptions for the Qoery SDK
"""


class QoeryError(Exception):
    """Base exception for all Qoery SDK errors"""
    pass


class AuthenticationError(QoeryError):
    """Raised when API key is missing or invalid"""
    pass


class InvalidRequestError(QoeryError):
    """Raised when the request parameters are invalid"""
    pass


class RateLimitError(QoeryError):
    """Raised when rate limit is exceeded"""
    pass


class APIError(QoeryError):
    """Raised when the API returns an unexpected error"""
    
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code
