"""
Django integration for autoapi-validator

Provides middleware and decorators for automatic request/response validation
in Django and Django REST Framework applications using OpenAPI schemas.
"""

from typing import Optional, Callable
import json
from functools import wraps

try:
    from django.http import JsonResponse, HttpRequest, HttpResponse
    from django.conf import settings
    from django.utils.decorators import method_decorator
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False

from ..validator import validate_response
from ..errors import ValidationError, OpenAPILoadError
from ..loader import load_openapi


class ValidationMiddleware:
    """
    Django middleware for automatic API request/response validation.
    
    Add to MIDDLEWARE in settings.py:
        MIDDLEWARE = [
            ...
            'autoapi_validator.integrations.django.ValidationMiddleware',
        ]
    
    Configure in settings.py:
        OPENAPI_SPEC_PATH = 'path/to/openapi.yaml'
        OPENAPI_VALIDATE_REQUESTS = False  # Optional
        OPENAPI_VALIDATE_RESPONSES = True  # Optional
    """
    
    def __init__(self, get_response):
        """Initialize middleware"""
        if not DJANGO_AVAILABLE:
            raise ImportError("Django is required for Django integration")
        
        self.get_response = get_response
        self._openapi_schema = None
        
        # Get configuration from Django settings
        self.spec_path = getattr(settings, 'OPENAPI_SPEC_PATH', None)
        self.validate_requests = getattr(settings, 'OPENAPI_VALIDATE_REQUESTS', False)
        self.validate_responses = getattr(settings, 'OPENAPI_VALIDATE_RESPONSES', True)
    
    @property
    def openapi_schema(self):
        """Lazy load OpenAPI schema"""
        if self._openapi_schema is None and self.spec_path:
            try:
                self._openapi_schema = load_openapi(self.spec_path)
            except Exception as e:
                raise OpenAPILoadError(f"Failed to load OpenAPI spec: {e}")
        return self._openapi_schema
    
    def __call__(self, request: HttpRequest):
        """Process request and response"""
        # Validate request if enabled
        if self.validate_requests and request.method in ['POST', 'PUT', 'PATCH']:
            validation_error = self._validate_request(request)
            if validation_error:
                return validation_error
        
        # Get response
        response = self.get_response(request)
        
        # Validate response if enabled
        if self.validate_responses:
            self._validate_response(request, response)
        
        return response
    
    def _validate_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Validate request body"""
        try:
            # Get request schema
            schema = self._get_request_schema(request.method, request.path)
            if not schema:
                return None  # No schema, skip validation
            
            # Parse request body
            try:
                if request.content_type == 'application/json':
                    request_data = json.loads(request.body)
                else:
                    return None  # Not JSON, skip
            except json.JSONDecodeError:
                return JsonResponse(
                    {"error": "Invalid JSON in request body"},
                    status=400
                )
            
            # Validate
            is_valid, message = validate_response(request_data, schema)
            
            if not is_valid:
                return JsonResponse(
                    {"error": "Request Validation Failed", "detail": message},
                    status=422
                )
        
        except Exception as e:
            print(f"[ERROR] Request validation error: {e}")
        
        return None
    
    def _validate_response(self, request: HttpRequest, response: HttpResponse):
        """Validate response body"""
        try:
            # Only validate JSON responses
            if not response.get('Content-Type', '').startswith('application/json'):
                return
            
            # Get response schema
            schema = self._get_response_schema(
                request.method,
                request.path,
                response.status_code
            )
            
            if not schema:
                return
            
            # Parse response
            try:
                response_data = json.loads(response.content)
            except (json.JSONDecodeError, AttributeError):
                return
            
            # Validate
            is_valid, message = validate_response(response_data, schema)
            
            if not is_valid:
                print(f"[WARNING] Response validation failed for {request.path}: {message}")
        
        except Exception as e:
            print(f"[ERROR] Response validation error: {e}")
    
    def _get_request_schema(self, method: str, path: str) -> Optional[dict]:
        """Get request schema from OpenAPI spec"""
        try:
            schema = self.openapi_schema
            if not schema:
                return None
            
            paths = schema.get("paths", {})
            path_item = self._find_matching_path(paths, path)
            
            if not path_item:
                return None
            
            operation = path_item.get(method.lower())
            if not operation:
                return None
            
            request_body = operation.get("requestBody", {})
            content = request_body.get("content", {})
            json_content = content.get("application/json", {})
            req_schema = json_content.get("schema", {})
            
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
            path_item = self._find_matching_path(paths, path)
            
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
            
            if "$ref" in resp_schema:
                resp_schema = self._resolve_ref(resp_schema["$ref"])
            
            return resp_schema if resp_schema else None
        
        except Exception:
            return None
    
    def _find_matching_path(self, paths: dict, actual_path: str) -> Optional[dict]:
        """Find matching path in OpenAPI spec"""
        # Try exact match first
        if actual_path in paths:
            return paths[actual_path]
        
        # Try matching with parameters
        for spec_path, path_item in paths.items():
            if self._match_path(actual_path, spec_path):
                return path_item
        
        return None
    
    def _match_path(self, actual_path: str, spec_path: str) -> bool:
        """Match Django path with OpenAPI path"""
        actual_parts = actual_path.strip("/").split("/")
        spec_parts = spec_path.strip("/").split("/")
        
        if len(actual_parts) != len(spec_parts):
            return False
        
        for actual, spec in zip(actual_parts, spec_parts):
            if spec.startswith("{") and spec.endswith("}"):
                continue
            if actual != spec:
                return False
        
        return True
    
    def _resolve_ref(self, ref: str) -> dict:
        """Resolve $ref in schema"""
        if not ref.startswith("#/"):
            return {}
        
        parts = ref[2:].split("/")
        schema = self.openapi_schema
        
        for part in parts:
            schema = schema.get(part, {})
        
        return schema


def validate_api(endpoint_path: str, method: Optional[str] = None, 
                 validate_request: bool = True, validate_response: bool = True):
    """
    Decorator for validating Django views against OpenAPI schema.
    
    Args:
        endpoint_path: OpenAPI path (e.g., "/users/{id}")
        method: HTTP method (if None, uses request.method)
        validate_request: Whether to validate request
        validate_response: Whether to validate response
    
    Example:
        @validate_api("/users", "POST")
        def create_user(request):
            return JsonResponse({"id": 1, "name": "John"})
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not DJANGO_AVAILABLE:
                return view_func(request, *args, **kwargs)
            
            # Get OpenAPI spec
            spec_path = getattr(settings, 'OPENAPI_SPEC_PATH', None)
            if not spec_path:
                # No spec configured, skip validation
                return view_func(request, *args, **kwargs)
            
            try:
                spec = load_openapi(spec_path)
            except Exception:
                return view_func(request, *args, **kwargs)
            
            # Determine method
            req_method = method or request.method
            
            # Validate request
            if validate_request and req_method in ['POST', 'PUT', 'PATCH']:
                error_response = _validate_request_body(request, spec, endpoint_path, req_method)
                if error_response:
                    return error_response
            
            # Get response
            response = view_func(request, *args, **kwargs)
            
            # Validate response
            if validate_response:
                _validate_response_body(response, spec, endpoint_path, req_method)
            
            return response
        
        return wrapped_view
    return decorator


def _validate_request_body(request, spec, path, method):
    """Helper to validate request body"""
    try:
        # Get schema
        paths = spec.get("paths", {})
        path_item = paths.get(path)
        
        if not path_item:
            return None
        
        operation = path_item.get(method.lower())
        if not operation:
            return None
        
        request_body = operation.get("requestBody", {})
        content = request_body.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})
        
        if not schema:
            return None
        
        # Resolve $ref
        if "$ref" in schema:
            ref = schema["$ref"]
            if ref.startswith("#/"):
                parts = ref[2:].split("/")
                schema = spec
                for part in parts:
                    schema = schema.get(part, {})
        
        # Parse request
        if request.content_type != 'application/json':
            return None
        
        try:
            request_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        # Validate
        is_valid, message = validate_response(request_data, schema)
        
        if not is_valid:
            return JsonResponse(
                {"error": "Request Validation Failed", "detail": message},
                status=422
            )
    
    except Exception as e:
        print(f"[ERROR] Request validation: {e}")
    
    return None


def _validate_response_body(response, spec, path, method):
    """Helper to validate response body"""
    try:
        if not response.get('Content-Type', '').startswith('application/json'):
            return
        
        # Get schema
        paths = spec.get("paths", {})
        path_item = paths.get(path)
        
        if not path_item:
            return
        
        operation = path_item.get(method.lower())
        if not operation:
            return
        
        responses = operation.get("responses", {})
        response_spec = responses.get(str(response.status_code)) or responses.get("default")
        
        if not response_spec:
            return
        
        content = response_spec.get("content", {})
        json_content = content.get("application/json", {})
        schema = json_content.get("schema", {})
        
        if not schema:
            return
        
        # Resolve $ref
        if "$ref" in schema:
            ref = schema["$ref"]
            if ref.startswith("#/"):
                parts = ref[2:].split("/")
                schema_obj = spec
                for part in parts:
                    schema_obj = schema_obj.get(part, {})
                schema = schema_obj
        
        # Parse response
        try:
            response_data = json.loads(response.content)
        except (json.JSONDecodeError, AttributeError):
            return
        
        # Validate
        is_valid, message = validate_response(response_data, schema)
        
        if not is_valid:
            print(f"[WARNING] Response validation failed: {message}")
    
    except Exception as e:
        print(f"[ERROR] Response validation: {e}")
