"""
LTFI-WSAP SDK Exceptions
"""


class WSAPException(Exception):
    """Base exception for LTFI-WSAP SDK"""
    pass


class AuthenticationError(WSAPException):
    """Authentication failed"""
    pass


class ValidationError(WSAPException):
    """Validation error"""
    pass


class NotFoundError(WSAPException):
    """Resource not found"""
    pass


class RateLimitError(WSAPException):
    """Rate limit exceeded"""
    pass