"""
Custom exception classes for autoapi-validator
"""


class OpenAPIError(Exception):
    """Base exception class for OpenAPI validation errors"""
    pass


class OpenAPILoadError(OpenAPIError):
    """Raised when OpenAPI spec file cannot be loaded"""
    pass


class ValidationError(OpenAPIError):
    """Raised when API response validation fails"""
    pass
