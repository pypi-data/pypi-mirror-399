"""
API response validator module

Validates API responses against JSON schemas defined in OpenAPI specifications.
"""

from jsonschema import validate
from jsonschema.exceptions import ValidationError as JsonSchemaValidationError
from .errors import ValidationError


def validate_response(response_json, schema):
    """
    Validate API response against a JSON schema.
    
    Args:
        response_json (dict): The API response data to validate
        schema (dict): JSON Schema definition from OpenAPI spec
        
    Returns:
        tuple: (is_valid: bool, message: str)
            - is_valid: True if validation passed, False otherwise
            - message: Success message or detailed error message
            
    Examples:
        >>> schema = {"type": "object", "properties": {"id": {"type": "integer"}}}
        >>> response = {"id": 1}
        >>> is_valid, msg = validate_response(response, schema)
        >>> print(is_valid)  # True
    """
    try:
        validate(instance=response_json, schema=schema)
        return True, "[OK] Valid response - matches schema"
    except JsonSchemaValidationError as e:
        # Format error message for better readability
        error_msg = f"[FAIL] Validation failed: {e.message}"
        if e.path:
            path = ".".join(str(p) for p in e.path)
            error_msg += f"\n  Path: {path}"
        if e.schema_path:
            schema_path = ".".join(str(p) for p in e.schema_path)
            error_msg += f"\n  Schema path: {schema_path}"
        return False, error_msg


def validate_response_strict(response_json, schema):
    """
    Validate API response with strict mode (raises exception on failure).
    
    Args:
        response_json (dict): The API response data to validate
        schema (dict): JSON Schema definition from OpenAPI spec
        
    Raises:
        ValidationError: If validation fails
        
    Examples:
        >>> schema = {"type": "object", "properties": {"id": {"type": "integer"}}}
        >>> response = {"id": "invalid"}
        >>> validate_response_strict(response, schema)  # raises ValidationError
    """
    try:
        validate(instance=response_json, schema=schema)
    except JsonSchemaValidationError as e:
        raise ValidationError(f"Response validation failed: {e.message}")
