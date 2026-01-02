"""
AutoAPI Validator - Automatic OpenAPI request & response validator

A Python package that automatically validates API requests & responses 
using an OpenAPI (Swagger) file.
"""

__version__ = "0.1.0"

from .loader import load_openapi
from .validator import validate_response
from .errors import OpenAPIError

__all__ = ["load_openapi", "validate_response", "OpenAPIError"]
