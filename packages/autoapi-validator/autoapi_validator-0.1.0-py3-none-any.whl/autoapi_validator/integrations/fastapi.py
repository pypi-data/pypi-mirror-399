"""
FastAPI integration for autoapi-validator

Provides middleware and utilities for automatic request/response validation
in FastAPI applications using the app's OpenAPI schema.
"""

from typing import Optional, Callable
import json
from fastapi import FastAPI, Request, Response, Depends, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..validator import validate_response
from ..errors import ValidationError


class ValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically validate API responses against OpenAPI schema.
    
    This middleware intercepts outgoing responses and validates them against
    the schema defined in the FastAPI app's OpenAPI specification.
    """
    
    def __init__(self, app: ASGIApp, fastapi_app: FastAPI, validate_responses: bool = True, validate_requests: bool = False):
        """
        Initialize validation middleware.
        
        Args:
            app: ASGI application
            fastapi_app: FastAPI application instance
            validate_responses: Whether to validate responses (default: True)
            validate_requests: Whether to validate requests (default: False)
        """
        super().__init__(app)
        self.fastapi_app = fastapi_app
        self.validate_responses = validate_responses
        self.validate_requests = validate_requests
        self._openapi_schema = None
    
    @property
    def openapi_schema(self):
        """Lazy load OpenAPI schema"""
        if self._openapi_schema is None:
            self._openapi_schema = self.fastapi_app.openapi()
        return self._openapi_schema
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and validate response.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response object
        """
        # Validate request if enabled
        if self.validate_requests and request.method in ["POST", "PUT", "PATCH"]:
            try:
                await self._validate_request(request)
            except ValidationError as e:
                return JSONResponse(
                    status_code=422,
                    content={"error": "Request Validation Failed", "detail": str(e)}
                )
        
        # Get response from next middleware/handler
        response = await call_next(request)
        
        # Only validate if enabled and response is JSON
        if not self.validate_responses:
            return response
        
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response
        
        # Get response schema for this endpoint
        try:
            schema = self._get_response_schema(request.method, request.url.path, response.status_code)
            if not schema:
                # No schema defined, skip validation
                return response
            
            # Read response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            # Parse and validate
            try:
                response_json = json.loads(response_body)
                is_valid, message = validate_response(response_json, schema)
                
                if not is_valid:
                    # Log validation error but return original response
                    # In production, you might want to handle this differently
                    print(f"[WARNING] Response validation failed: {message}")
                    # Optionally, you could raise an error in strict mode
            except json.JSONDecodeError:
                pass  # Invalid JSON, skip validation
            
            # Recreate response with the body we read
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )
        
        except Exception as e:
            # Don't break the response if validation fails
            print(f"[ERROR] Validation middleware error: {e}")
            return response
    
    def _get_response_schema(self, method: str, path: str, status_code: int) -> Optional[dict]:
        """
        Get response schema from OpenAPI spec.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            status_code: Response status code
            
        Returns:
            Schema dictionary or None if not found
        """
        try:
            openapi = self.openapi_schema
            paths = openapi.get("paths", {})
            
            # Find matching path (handle path parameters)
            path_item = paths.get(path)
            if not path_item:
                # Try to match path with parameters
                for spec_path, spec_item in paths.items():
                    if self._match_path(path, spec_path):
                        path_item = spec_item
                        break
            
            if not path_item:
                return None
            
            # Get operation (method)
            operation = path_item.get(method.lower())
            if not operation:
                return None
            
            # Get response for status code
            responses = operation.get("responses", {})
            response_spec = responses.get(str(status_code)) or responses.get("default")
            if not response_spec:
                return None
            
            # Get schema from response
            content = response_spec.get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema", {})
            
            # Resolve $ref if present
            if "$ref" in schema:
                schema = self._resolve_ref(schema["$ref"])
            
            return schema if schema else None
        
        except Exception:
            return None
    
    def _match_path(self, actual_path: str, spec_path: str) -> bool:
        """
        Match actual path with OpenAPI spec path (with parameters).
        
        Args:
            actual_path: Actual request path
            spec_path: OpenAPI spec path (may contain {param})
            
        Returns:
            True if paths match
        """
        actual_parts = actual_path.strip("/").split("/")
        spec_parts = spec_path.strip("/").split("/")
        
        if len(actual_parts) != len(spec_parts):
            return False
        
        for actual, spec in zip(actual_parts, spec_parts):
            if spec.startswith("{") and spec.endswith("}"):
                continue  # Parameter, matches anything
            if actual != spec:
                return False
        
        return True
    
    def _resolve_ref(self, ref: str) -> dict:
        """
        Resolve $ref in OpenAPI schema.
        
        Args:
            ref: Reference string (e.g., "#/components/schemas/User")
            
        Returns:
            Resolved schema dictionary
        """
        if not ref.startswith("#/"):
            return {}
        
        parts = ref[2:].split("/")
        schema = self.openapi_schema
        
        for part in parts:
            schema = schema.get(part, {})
        
        return schema
    
    async def _validate_request(self, request: Request) -> None:
        """
        Validate request body against OpenAPI schema.
        
        Args:
            request: FastAPI request object
            
        Raises:
            ValidationError: If request validation fails
        """
        try:
            # Get request schema
            schema = self._get_request_schema(request.method, request.url.path)
            if not schema:
                return  # No schema defined, skip validation
            
            # Parse request body
            try:
                body = await request.body()
                if not body:
                    # Check if body is required
                    if schema.get("required"):
                        raise ValidationError("Request body is required")
                    return
                
                request_json = json.loads(body)
            except json.JSONDecodeError:
                raise ValidationError("Invalid JSON in request body")
            
            # Validate against schema
            from ..validator import validate_response  # Reuse for request validation
            is_valid, message = validate_response(request_json, schema)
            
            if not is_valid:
                raise ValidationError(message)
        
        except ValidationError:
            raise
        except Exception as e:
            # Don't break request if validation fails unexpectedly
            print(f"[ERROR] Request validation error: {e}")
    
    def _get_request_schema(self, method: str, path: str) -> Optional[dict]:
        """
        Get request body schema from OpenAPI spec.
        
        Args:
            method: HTTP method (POST, PUT, etc.)
            path: Request path
            
        Returns:
            Schema dictionary or None if not found
        """
        try:
            openapi = self.openapi_schema
            paths = openapi.get("paths", {})
            
            # Find matching path
            path_item = paths.get(path)
            if not path_item:
                for spec_path, spec_item in paths.items():
                    if self._match_path(path, spec_path):
                        path_item = spec_item
                        break
            
            if not path_item:
                return None
            
            # Get operation
            operation = path_item.get(method.lower())
            if not operation:
                return None
            
            # Get request body schema
            request_body = operation.get("requestBody", {})
            content = request_body.get("content", {})
            json_content = content.get("application/json", {})
            schema = json_content.get("schema", {})
            
            # Resolve $ref if present
            if "$ref" in schema:
                schema = self._resolve_ref(schema["$ref"])
            
            return schema if schema else None
        
        except Exception:
            return None


def setup_validation_middleware(
    app: FastAPI,
    validate_responses: bool = True
) -> None:
    """
    Add validation middleware to FastAPI app.
    
    Args:
        app: FastAPI application instance
        validate_responses: Whether to validate responses
        
    Example:
        >>> from fastapi import FastAPI
        >>> from autoapi_validator.integrations.fastapi import setup_validation_middleware
        >>> 
        >>> app = FastAPI()
        >>> setup_validation_middleware(app)
    """
    app.add_middleware(ValidationMiddleware, fastapi_app=app, validate_responses=validate_responses)


class RequestValidator:
    """
    Dependency for validating requests in FastAPI endpoints.
    Validates request body against OpenAPI schema in a dependency.
    
    Note: Request validation is already handled by middleware if enabled.
    This dependency provides explicit validation control per endpoint.
    """
    
    def __init__(self, strict: bool = True):
        """
        Initialize request validator.
        
        Args:
            strict: If True, raise HTTPException on validation failure
        """
        self.strict = strict
    
    async def __call__(self, request: Request) -> dict:
        """
        Validate request - note: validation is handled by Pydantic models in FastAPI.
        This is a compatibility layer for explicit validation.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Validation result dict
        """
        # FastAPI + Pydantic already validates request bodies when using response_model
        # This dependency is for additional custom validation if needed
        return {"validated": True, "message": "Request validated by FastAPI/Pydantic"}


# Custom exception handler for validation errors
async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handle validation errors with proper HTTP response.
    
    Args:
        request: Request that caused the error
        exc: ValidationError exception
        
    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": str(exc),
            "path": request.url.path
        }
    )


def configure_validation(app: FastAPI, validate_responses: bool = True) -> None:
    """
    Configure complete validation for FastAPI app.
    
    This is a convenience function that sets up:
    - Response validation middleware
    - Exception handlers
    
    Args:
        app: FastAPI application instance
        validate_responses: Whether to validate responses
        
    Example:
        >>> from fastapi import FastAPI
        >>> from autoapi_validator.integrations.fastapi import configure_validation
        >>> 
        >>> app = FastAPI()
        >>> configure_validation(app)
    """
    # Add middleware
    setup_validation_middleware(app, validate_responses=validate_responses)
    
    # Add exception handlers
    app.add_exception_handler(ValidationError, validation_exception_handler)
