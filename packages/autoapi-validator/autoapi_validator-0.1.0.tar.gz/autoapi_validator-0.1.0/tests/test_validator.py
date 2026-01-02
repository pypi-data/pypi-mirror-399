"""
Basic tests for autoapi-validator
"""

import pytest
from autoapi_validator import validate_response, OpenAPIError


def test_validate_response_valid():
    """Test validation with valid data"""
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        },
        "required": ["id", "name"]
    }
    
    response = {
        "id": 1,
        "name": "Santhosh"
    }
    
    is_valid, message = validate_response(response, schema)
    assert is_valid is True
    assert "Valid" in message


def test_validate_response_invalid_type():
    """Test validation with wrong data type"""
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        }
    }
    
    response = {
        "id": "one",  # Should be integer
        "name": "Santhosh"
    }
    
    is_valid, message = validate_response(response, schema)
    assert is_valid is False
    assert "Validation failed" in message


def test_validate_response_missing_required():
    """Test validation with missing required field"""
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"}
        },
        "required": ["id", "name"]
    }
    
    response = {
        "id": 1
        # Missing 'name'
    }
    
    is_valid, message = validate_response(response, schema)
    assert is_valid is False


def test_validate_response_extra_properties():
    """Test validation with extra properties (should pass by default)"""
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"}
        }
    }
    
    response = {
        "id": 1,
        "extra_field": "value"
    }
    
    is_valid, message = validate_response(response, schema)
    assert is_valid is True
