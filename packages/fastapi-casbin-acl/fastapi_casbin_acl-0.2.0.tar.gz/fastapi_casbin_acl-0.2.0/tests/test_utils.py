"""
Tests for fastapi_casbin_acl.utils module.
"""

import pytest
from fastapi import FastAPI, Request, Depends
from httpx import AsyncClient, ASGITransport
from fastapi_casbin_acl.utils import resolve_subject, ensure_acl_initialized
from fastapi_casbin_acl.enforcer import acl
from fastapi_casbin_acl.config import ACLConfig
from fastapi_casbin_acl.exceptions import ACLNotInitialized
import casbin
import os


@pytest.fixture
async def setup_acl():
    """Setup ACL for testing."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)
    config = ACLConfig()
    await acl.init(adapter=adapter, models=["permission_rbac"], config=config)
    yield acl
    acl._enforcers = {}
    acl._adapters = {}
    acl._config = None
    acl._initialized = False


@pytest.mark.asyncio
async def test_resolve_subject_with_request_param():
    """Test resolve_subject with function that accepts request parameter."""
    app = FastAPI()

    def get_user(request: Request):
        return request.headers.get("X-User")

    @app.get("/test")
    async def test_route(request: Request):
        sub = await resolve_subject(request, get_user)
        return {"subject": sub}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/test", headers={"X-User": "alice"})
        assert response.status_code == 200
        assert response.json()["subject"] == "alice"


@pytest.mark.asyncio
async def test_resolve_subject_with_no_params():
    """Test resolve_subject with function that accepts no parameters."""
    app = FastAPI()

    def get_user():
        return "alice"

    @app.get("/test")
    async def test_route(request: Request):
        sub = await resolve_subject(request, get_user)
        return {"subject": sub}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/test")
        assert response.status_code == 200
        assert response.json()["subject"] == "alice"


@pytest.mark.asyncio
async def test_resolve_subject_with_async_function():
    """Test resolve_subject with async function."""
    app = FastAPI()

    async def get_user(request: Request):
        return request.headers.get("X-User")

    @app.get("/test")
    async def test_route(request: Request):
        sub = await resolve_subject(request, get_user)
        return {"subject": sub}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/test", headers={"X-User": "bob"})
        assert response.status_code == 200
        assert response.json()["subject"] == "bob"


@pytest.mark.asyncio
async def test_resolve_subject_returns_none():
    """Test resolve_subject when function returns None."""
    app = FastAPI()

    def get_user(request: Request):
        return None

    @app.get("/test")
    async def test_route(request: Request):
        sub = await resolve_subject(request, get_user)
        return {"subject": sub}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/test")
        assert response.status_code == 200
        assert response.json()["subject"] is None


@pytest.mark.asyncio
async def test_resolve_subject_converts_to_string():
    """Test resolve_subject converts result to string."""
    app = FastAPI()

    def get_user(request: Request):
        return 123  # Return integer

    @app.get("/test")
    async def test_route(request: Request):
        sub = await resolve_subject(request, get_user)
        return {"subject": sub, "type": type(sub).__name__}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/test")
        assert response.status_code == 200
        assert response.json()["subject"] == "123"
        assert response.json()["type"] == "str"


@pytest.mark.asyncio
async def test_resolve_subject_handles_exception():
    """Test resolve_subject returns None when function raises exception."""
    app = FastAPI()

    def get_user(request: Request):
        raise ValueError("Error getting user")

    @app.get("/test")
    async def test_route(request: Request):
        sub = await resolve_subject(request, get_user)
        return {"subject": sub}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/test")
        assert response.status_code == 200
        assert response.json()["subject"] is None


@pytest.mark.asyncio
async def test_ensure_acl_initialized_success(setup_acl):
    """Test ensure_acl_initialized passes when ACL is initialized."""
    app = FastAPI()

    @app.get("/test")
    async def test_route(_: None = Depends(ensure_acl_initialized)):
        return {"message": "ok"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/test")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_ensure_acl_initialized_failure():
    """Test ensure_acl_initialized raises HTTPException when ACL not initialized."""
    # Reset ACL state
    acl._enforcers = {}
    acl._adapters = {}
    acl._config = None
    acl._initialized = False

    app = FastAPI()

    @app.get("/test")
    async def test_route(_: None = Depends(ensure_acl_initialized)):
        return {"message": "ok"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/test")
        assert response.status_code == 500
        assert "not initialized" in response.json()["detail"].lower()

