"""
Tests for fastapi_casbin_acl.exception_handlers module.
"""

import pytest
from fastapi import FastAPI, Request
from httpx import AsyncClient, ASGITransport
from fastapi_casbin_acl.exceptions import Unauthorized, Forbidden
from fastapi_casbin_acl.exception_handlers import (
    unauthorized_handler,
    forbidden_handler,
)


@pytest.mark.asyncio
async def test_unauthorized_handler():
    """Test unauthorized_handler returns 401 with proper message."""
    app = FastAPI()
    app.add_exception_handler(Unauthorized, unauthorized_handler)

    @app.get("/protected")
    async def protected_route():
        raise Unauthorized("User not authenticated")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/protected")
        assert response.status_code == 401
        data = response.json()
        assert "Unauthorized" in data["message"]
        assert "authentication" in data["detail"].lower()


@pytest.mark.asyncio
async def test_forbidden_handler():
    """Test forbidden_handler returns 403 with proper message."""
    app = FastAPI()
    app.add_exception_handler(Forbidden, forbidden_handler)

    @app.get("/protected")
    async def protected_route():
        raise Forbidden("Permission denied")

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/protected")
        assert response.status_code == 403
        data = response.json()
        assert "Forbidden" in data["message"]
        assert "permission" in data["detail"].lower()

