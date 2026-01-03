"""
Tests for fastapi_casbin_acl.dependency module.
"""

import pytest
from fastapi import FastAPI, Request, Depends
from httpx import AsyncClient, ASGITransport
from fastapi_casbin_acl.dependency import permission_required
from fastapi_casbin_acl.enforcer import acl
from fastapi_casbin_acl.config import ACLConfig
from fastapi_casbin_acl.exceptions import Unauthorized, Forbidden
from fastapi_casbin_acl.exception_handlers import (
    unauthorized_handler,
    forbidden_handler,
)
import casbin
import os


@pytest.fixture
async def setup_rbac_acl():
    """Setup ACL with RBAC model for testing."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)

    config = ACLConfig()
    await acl.init(adapter=adapter, models=["permission_rbac"], config=config)
    yield acl
    acl._enforcers = {}
    acl._adapters = {}
    acl._config = None
    acl._initialized = False


@pytest.fixture
async def setup_abac_acl():
    """Setup ACL with ABAC model for testing."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)

    config = ACLConfig()
    await acl.init(adapter=adapter, models=["abac"], config=config)
    yield acl
    acl._enforcers = {}
    acl._adapters = {}
    acl._config = None
    acl._initialized = False


def get_current_user(request: Request):
    """Mock subject getter."""
    return request.headers.get("X-User")


class MockResource:
    """Mock resource with owner_id."""

    def __init__(self, owner_id):
        self.owner_id = owner_id


def get_sync_resource(request: Request):
    """Synchronous resource getter."""
    owner = request.headers.get("X-Resource-Owner")
    if owner:
        return MockResource(owner_id=owner)
    return None


async def get_async_resource(request: Request):
    """Asynchronous resource getter."""
    owner = request.headers.get("X-Resource-Owner")
    if owner:
        return MockResource(owner_id=owner)
    return None


@pytest.mark.asyncio
async def test_dependency_rbac_enforce_3_args(setup_rbac_acl):
    """Test RBAC model uses 3-arg enforce (sub, obj, act)."""
    # Add g2 mapping: route name -> permission
    enforcer = acl.get_enforcer("permission_rbac")
    await enforcer.add_named_grouping_policy("g2", "test_route", "/public")

    app = FastAPI()

    @app.get("/public")
    async def test_route(
        request: Request,
        _=Depends(permission_required(get_subject=get_current_user, action="read")),
    ):
        return {"message": "ok"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Alice has policy for /public read in RBAC model
        # This tests the RBAC enforce path (3 args, no owner)
        response = await client.get("/public", headers={"X-User": "alice"})
        assert response.status_code == 200


# NOTE: These tests are disabled because permission_required currently only supports
# Permission RBAC model and does not support 'model' or 'resource' parameters.
# These tests may be re-enabled when ABAC support is added to permission_required.

# @pytest.mark.asyncio
# async def test_dependency_fallback_to_url_path(setup_abac_acl):
#     """Test fallback to request.url.path when route is not APIRoute."""
#     app = FastAPI()
#
#     @app.get("/public")
#     async def test_route(
#         request: Request,
#         _=Depends(
#             permission_required(
#                 get_subject=get_current_user, action="read", model="abac"
#             )
#         ),
#     ):
#         return {"message": "ok"}
#
#     async with AsyncClient(
#         transport=ASGITransport(app=app), base_url="http://test"
#     ) as client:
#         # This should use route.path_format (not fallback)
#         response = await client.get("/public", headers={"X-User": "alice"})
#         assert response.status_code == 200


# @pytest.mark.asyncio
# async def test_dependency_async_resource_getter(setup_abac_acl):
#     """Test async resource getter."""
#     app = FastAPI()
#
#     @app.get("/orders/{id}")
#     async def get_order(
#         request: Request,
#         id: str,
#         _=Depends(
#             permission_required(
#                 get_subject=get_current_user,
#                 resource=get_async_resource,
#                 action="read",
#                 model="abac",
#             )
#         ),
#     ):
#         return {"message": f"order {id}"}
#
#     async with AsyncClient(
#         transport=ASGITransport(app=app), base_url="http://test"
#     ) as client:
#         # Dave is owner
#         response = await client.get(
#             "/orders/123", headers={"X-User": "dave", "X-Resource-Owner": "dave"}
#         )
#         assert response.status_code == 200


@pytest.mark.asyncio
async def test_dependency_rbac_model_no_owner_param(setup_rbac_acl):
    """Test RBAC model enforce without owner parameter."""
    # Add g2 mapping: route name -> permission
    enforcer = acl.get_enforcer("permission_rbac")
    await enforcer.add_named_grouping_policy("g2", "get_public", "/public")

    app = FastAPI()

    @app.get("/public")
    async def get_public(
        request: Request,
        _=Depends(permission_required(get_subject=get_current_user, action="read")),
    ):
        return {"message": "public"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Alice has policy for /public read in RBAC model
        response = await client.get("/public", headers={"X-User": "alice"})
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_dependency_unauthorized_user(setup_rbac_acl):
    """Test permission_required raises Unauthorized when user is not authenticated."""
    enforcer = acl.get_enforcer("permission_rbac")
    await enforcer.add_named_grouping_policy("g2", "test_route", "/public")

    app = FastAPI()
    app.add_exception_handler(Unauthorized, unauthorized_handler)

    @app.get("/public")
    async def test_route(
        request: Request,
        _=Depends(permission_required(get_subject=get_current_user, action="read")),
    ):
        return {"message": "ok"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # No X-User header, should raise Unauthorized
        response = await client.get("/public")
        assert response.status_code == 401
        assert "Unauthorized" in response.text


@pytest.mark.asyncio
async def test_dependency_no_permission_mapping(setup_rbac_acl):
    """Test permission_required raises Forbidden when no permission mapping found."""
    app = FastAPI()
    app.add_exception_handler(Forbidden, forbidden_handler)

    @app.get("/public")
    async def test_route(
        request: Request,
        _=Depends(permission_required(get_subject=get_current_user, action="read")),
    ):
        return {"message": "ok"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # No g2 mapping for test_route, should raise Forbidden
        response = await client.get("/public", headers={"X-User": "alice"})
        assert response.status_code == 403
        data = response.json()
        assert "Forbidden" in data["message"] or "No permission mapping found" in str(
            data
        )


@pytest.mark.asyncio
async def test_dependency_permission_denied(setup_rbac_acl):
    """Test permission_required raises Forbidden when permission is denied."""
    enforcer = acl.get_enforcer("permission_rbac")
    await enforcer.add_named_grouping_policy("g2", "test_route", "/public")

    # Remove bob's permission for /public read (policy.csv has bob with /public read)
    # We need to remove it to test permission denied
    await enforcer.remove_named_policy("p", "bob", "/public", "read")

    app = FastAPI()
    app.add_exception_handler(Forbidden, forbidden_handler)

    @app.get("/public")
    async def test_route(
        request: Request,
        _=Depends(permission_required(get_subject=get_current_user, action="read")),
    ):
        return {"message": "ok"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Bob doesn't have permission for /public read, should raise Forbidden
        response = await client.get("/public", headers={"X-User": "bob"})
        assert response.status_code == 403
        data = response.json()
        assert "Forbidden" in data["message"]


@pytest.mark.asyncio
async def test_dependency_policy_permission_required(setup_rbac_acl):
    """Test policy_permission_required dependency."""
    from fastapi_casbin_acl.dependency import policy_permission_required

    # Update acl config with policy router enabled
    acl._config.policy_router_enable = True
    acl._config.get_subject = get_current_user

    # Add policy for alice to have policy_management permission
    enforcer = acl.get_enforcer("permission_rbac")
    await enforcer.add_named_policy("p", "alice", "policy_management", "write")

    app = FastAPI()

    @app.get("/policy")
    async def get_policy(
        request: Request,
        _=Depends(policy_permission_required),
    ):
        return {"message": "policy"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Alice has policy_management write permission
        response = await client.get("/policy", headers={"X-User": "alice"})
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_dependency_policy_permission_required_unauthorized(setup_rbac_acl):
    """Test policy_permission_required raises Unauthorized when user not authenticated."""
    from fastapi_casbin_acl.dependency import policy_permission_required

    # Update acl config with policy router enabled
    acl._config.policy_router_enable = True
    acl._config.get_subject = get_current_user

    app = FastAPI()
    app.add_exception_handler(Unauthorized, unauthorized_handler)

    @app.get("/policy")
    async def get_policy(
        request: Request,
        _=Depends(policy_permission_required),
    ):
        return {"message": "policy"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # No X-User header, should raise Unauthorized
        response = await client.get("/policy")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_dependency_policy_permission_required_forbidden(setup_rbac_acl):
    """Test policy_permission_required raises Forbidden when permission denied."""
    from fastapi_casbin_acl.dependency import policy_permission_required

    # Update acl config with policy router enabled
    acl._config.policy_router_enable = True
    acl._config.get_subject = get_current_user

    app = FastAPI()
    app.add_exception_handler(Forbidden, forbidden_handler)

    @app.get("/policy")
    async def get_policy(
        request: Request,
        _=Depends(policy_permission_required),
    ):
        return {"message": "policy"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Bob doesn't have policy_management permission
        response = await client.get("/policy", headers={"X-User": "bob"})
        assert response.status_code == 403
        data = response.json()
        assert "Forbidden" in data["message"]


@pytest.mark.asyncio
async def test_dependency_policy_permission_required_disabled(setup_rbac_acl):
    """Test policy_permission_required passes when router protection is disabled."""
    from fastapi_casbin_acl.dependency import policy_permission_required

    # Update acl config with policy router disabled
    acl._config.policy_router_enable = False

    app = FastAPI()

    @app.get("/policy")
    async def get_policy(
        request: Request,
        _=Depends(policy_permission_required),
    ):
        return {"message": "policy"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Should pass when protection is disabled
        response = await client.get("/policy")
        assert response.status_code == 200
