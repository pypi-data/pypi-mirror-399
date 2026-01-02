"""
Flask integration for autoapi-validator

Provides decorators and utilities for automatic request/response validation
in Flask applications using OpenAPI schemas.
"""

from typing import Optional, Callable
import json
from functools import wraps
from flask import Flask, request, jsonify, Response

from ..validator import validate_response
from ..errors import ValidationError, OpenAPILoadError
from ..loader import load_openapi


class FlaskValidator:
    """
    Flask validation helper that integrates with Flask applications.
    
    Usage:
        >>> from flask import Flask
        >>> from autoapi_validator.integrations.flask import FlaskValidator
        >>> 
        >>> app = Flask(__name__)
        >>> validator = FlaskValidator(app, "openapi.yaml")
    """
    
    def __init__(self, app: Optional[Flask] = None, openapi_spec_path: Optional[str] = None):
        """
        Initialize Flask validator.
        
        Args:
            app: Flask application instance
            openapi_spec_path: Path to OpenAPI specification file
        """
        self.app = app
        self.openapi_spec_path = openapi_spec_path
        self._openapi_schema = None
        
        if app is not None:
            self.init_app(app, openapi_spec_path)
    
    def init_app(self, app: Flask, openapi_spec_path: Optional[str] = None):
        """
        Initialize validation for Flask app.
        
        Args:
            app: Flask application instance
            openapi_spec_path: Path to OpenAPI specification file
        """
        self.app = app
        if openapi_spec_path:
            self.openapi_spec_path = openapi_spec_path
        
        # Store validator in app config for access in decorators
        app.config['OPENAPI_VALIDATOR'] = self
    
    @property
    def openapi_schema(self):
        """Lazy load OpenAPI schema"""
        if self._openapi_schema is None and self.openapi_spec_path:
            try:
                self._openapi_schema = load_openapi(self.openapi_spec_path)
            except Exception as e:
                raise OpenAPILoadError(f"Failed to load OpenAPI spec: {e}")
        return self._openapi_schema
    
    def validate_request_decorator(self, endpoint_path: str, method: str = "POST"):
        """
        Decorator to validate request body against OpenAPI schema.
        
        Args:
            endpoint_path: OpenAPI path (e.g., "/users")
            method: HTTP method
            
        Example:
            >>> @app.post("/users")
            >>> @validator.validate_request_decorator("/users", "POST")
            >>> def create_user():
            >>>     return jsonify(request.json)
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # Get request schema
                schema = self._get_request_schema(method, endpoint_path)
                
                if schema:
                    # Validate request body
                    if not request.is_json:
                        return jsonify({"error": "Request must be JSON"}), 400
                    
                    try:
                        request_data = request.get_json()
                        is_valid, message = validate_response(request_data, schema)
                        
                        if not is_valid:
                            return jsonify({
                                "error": "Request Validation Failed",
                                "detail": message
                            }), 422
                    except Exception as e:
                        return jsonify({"error": f"Validation error: {str(e)}"}), 422
                
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    def validate_response_decorator(self, endpoint_path: str, method: str = "GET", status_code: int = 200):
        """
        Decorator to validate response body against OpenAPI schema.
        
        Args:
            endpoint_path: OpenAPI path
            method: HTTP method
            status_code: Expected status code
            
        Example:
            >>> @app.get("/users/<int:user_id>")
            >>> @validator.validate_response_decorator("/users/{user_id}", "GET")
            >>> def get_user(user_id):
            >>>     return jsonify({"id": user_id, "name": "John"})
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                response = f(*args, **kwargs)
                
                # Get response schema
                schema = self._get_response_schema(method, endpoint_path, status_code)
                
                if schema:
                    # Extract response data
                    if isinstance(response, tuple):
                        data, code = response[0], response[1] if len(response) > 1 else 200
                    else:
                        data, code = response, 200
                    
                    # Parse response data
                    if isinstance(data, Response):
                        try:
                            response_json = json.loads(data.get_data(as_text=True))
                        except:
                            return response  # Can't parse, skip validation
                    elif isinstance(data, dict):
                        response_json = data
                    else:
                        return response  # Not JSON, skip validation
                    
                    # Validate
                    is_valid, message = validate_response(response_json, schema)
                    
                    if not is_valid:
                        print(f"[WARNING] Response validation failed for {endpoint_path}: {message}")
                        # Log but don't block the response
                
                return response
            return decorated_function
        return decorator
    
    def _get_request_schema(self, method: str, path: str) -> Optional[dict]:
        """Get request body schema from OpenAPI spec"""
        try:
            schema = self.openapi_schema
            if not schema:
                return None
            
            paths = schema.get("paths", {})
            path_item = paths.get(path)
            
            if not path_item:
                return None
            
            operation = path_item.get(method.lower())
            if not operation:
                return None
            
            request_body = operation.get("requestBody", {})
            content = request_body.get("content", {})
            json_content = content.get("application/json", {})
            req_schema = json_content.get("schema", {})
            
            # Resolve $ref if present
            if "$ref" in req_schema:
                req_schema = self._resolve_ref(req_schema["$ref"])
            
            return req_schema if req_schema else None
        
        except Exception:
            return None
    
    def _get_response_schema(self, method: str, path: str, status_code: int) -> Optional[dict]:
        """Get response schema from OpenAPI spec"""
        try:
            schema = self.openapi_schema
            if not schema:
                return None
            
            paths = schema.get("paths", {})
            path_item = paths.get(path)
            
            if not path_item:
                return None
            
            operation = path_item.get(method.lower())
            if not operation:
                return None
            
            responses = operation.get("responses", {})
            response_spec = responses.get(str(status_code)) or responses.get("default")
            
            if not response_spec:
                return None
            
            content = response_spec.get("content", {})
            json_content = content.get("application/json", {})
            resp_schema = json_content.get("schema", {})
            
            # Resolve $ref if present
            if "$ref" in resp_schema:
                resp_schema = self._resolve_ref(resp_schema["$ref"])
            
            return resp_schema if resp_schema else None
        
        except Exception:
            return None
    
    def _resolve_ref(self, ref: str) -> dict:
        """Resolve $ref in schema"""
        if not ref.startswith("#/"):
            return {}
        
        parts = ref[2:].split("/")
        schema = self.openapi_schema
        
        for part in parts:
            schema = schema.get(part, {})
        
        return schema


def setup_flask_validation(app: Flask, openapi_spec_path: str) -> FlaskValidator:
    """
    Configure Flask app with validation support.
    
    Args:
        app: Flask application instance
        openapi_spec_path: Path to OpenAPI specification file
        
    Returns:
        FlaskValidator instance
        
    Example:
        >>> from flask import Flask
        >>> from autoapi_validator.integrations.flask import setup_flask_validation
        >>> 
        >>> app = Flask(__name__)
        >>> validator = setup_flask_validation(app, "openapi.yaml")
    """
    validator = FlaskValidator(app, openapi_spec_path)
    return validator


# Convenience decorators
def validate_request(endpoint_path: str, method: str = "POST"):
    """
    Standalone decorator for request validation.
    Requires FlaskValidator to be configured in app.config['OPENAPI_VALIDATOR']
    
    Example:
        >>> @app.post("/users")
        >>> @validate_request("/users", "POST")
        >>> def create_user():
        >>>     return jsonify(request.json)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import current_app
            validator = current_app.config.get('OPENAPI_VALIDATOR')
            
            if not validator:
                # No validator configured, skip validation
                return f(*args, **kwargs)
            
            return validator.validate_request_decorator(endpoint_path, method)(f)(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_response(endpoint_path: str, method: str = "GET", status_code: int = 200):
    """
    Standalone decorator for response validation.
    Requires FlaskValidator to be configured in app.config['OPENAPI_VALIDATOR']
    
    Example:
        >>> @app.get("/users/<int:user_id>")
        >>> @validate_response("/users/{user_id}", "GET")
        >>> def get_user(user_id):
        >>>     return jsonify({"id": user_id, "name": "John"})
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import current_app
            validator = current_app.config.get('OPENAPI_VALIDATOR')
            
            if not validator:
                return f(*args, **kwargs)
            
            return validator.validate_response_decorator(endpoint_path, method, status_code)(f)(*args, **kwargs)
        
        return decorated_function
    return decorator
