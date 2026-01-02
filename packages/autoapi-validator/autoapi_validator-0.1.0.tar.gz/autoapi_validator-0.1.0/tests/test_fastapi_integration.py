"""
Tests for FastAPI integration
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

# Only run these tests if FastAPI is installed
pytest.importorskip("fastapi")

from autoapi_validator.integrations.fastapi import (
    configure_validation,
    setup_validation_middleware,
    ValidationMiddleware
)


# Test models (rename to avoid pytest collection warnings)
class UserModel(BaseModel):
    id: int
    name: str
    email: str


class NewUserModel(BaseModel):
    name: str
    email: str


@pytest.fixture
def app():
    """Create test FastAPI app"""
    test_app = FastAPI()
    
    @test_app.get("/users/{user_id}", response_model=UserModel)
    async def get_user(user_id: int):
        return {
            "id": user_id,
            "name": "Test User",
            "email": "test@example.com"
        }
    
    @test_app.get("/users/{user_id}/invalid")
    async def get_invalid_user(user_id: int):
        # Returns invalid response (id as string instead of int)
        return {
            "id": "not-an-int",
            "name": "Test User",
            "email": "test@example.com"
        }
    
    @test_app.post("/users", response_model=UserModel, status_code=201)
    async def create_user(user: NewUserModel):
        return {
            "id": 1,
            "name": user.name,
            "email": user.email
        }
    
    return test_app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


def test_middleware_setup(app):
    """Test that middleware can be added to app"""
    initial_middleware_count = len(app.user_middleware)
    setup_validation_middleware(app)
    # Check that middleware was added
    assert len(app.user_middleware) > initial_middleware_count


def test_configure_validation(app):
    """Test complete validation configuration"""
    configure_validation(app)
    # Middleware should be added
    assert len(app.user_middleware) > 0


def test_valid_response(app, client):
    """Test that valid responses pass through"""
    configure_validation(app, validate_responses=True)
    
    response = client.get("/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"


def test_create_user(app, client):
    """Test POST endpoint with validation"""
    configure_validation(app, validate_responses=True)
    
    response = client.post("/users", json={
        "name": "New User",
        "email": "new@example.com"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "New User"


def test_middleware_with_invalid_response(app, client):
    """Test middleware behavior with invalid response"""
    configure_validation(app, validate_responses=True)
    
    # This endpoint returns invalid data, but FastAPI's pydantic validation
    # might catch it first. The middleware would log warnings.
    response = client.get("/users/1/invalid")
    
    # Response should still be returned (middleware logs warning but doesn't block)
    assert response.status_code == 200


def test_validation_disabled(app, client):
    """Test that validation can be disabled"""
    configure_validation(app, validate_responses=False)
    
    response = client.get("/users/1")
    assert response.status_code == 200


def test_openapi_schema_generated(app):
    """Test that OpenAPI schema is accessible"""
    configure_validation(app)
    
    schema = app.openapi()
    assert schema is not None
    assert "paths" in schema
    assert "/users/{user_id}" in schema["paths"]


def test_path_matching():
    """Test path matching with parameters"""
    from autoapi_validator.integrations.fastapi import ValidationMiddleware
    
    # Create a mock middleware instance
    class MockApp:
        def openapi(self):
            return {}
    
    middleware = ValidationMiddleware(app=None, fastapi_app=MockApp())
    
    # Test exact match
    assert middleware._match_path("/users/123", "/users/{user_id}")
    assert middleware._match_path("/users/123/posts/456", "/users/{user_id}/posts/{post_id}")
    
    # Test non-match
    assert not middleware._match_path("/users", "/users/{user_id}")
    assert not middleware._match_path("/users/123/posts", "/users/{user_id}")
