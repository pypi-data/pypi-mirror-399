"""
Tests for fastapi_casbin_acl.router.mappings module.
"""

import pytest
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
import casbin
import os
from fastapi_casbin_acl.enforcer import acl
from fastapi_casbin_acl.config import ACLConfig
from fastapi_casbin_acl.router.mappings import router
from fastapi_casbin_acl.dependency import policy_permission_required


@pytest.fixture
async def setup_acl_for_mappings():
    """Setup ACL for mappings tests."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)
    config = ACLConfig()
    config.policy_router_enable = True
    await acl.init(adapter=adapter, models=["permission_rbac"], config=config)
    yield acl
    acl._enforcers = {}
    acl._adapters = {}
    acl._config = None
    acl._initialized = False


@pytest.fixture
async def app_with_mappings_router(setup_acl_for_mappings):
    """Create FastAPI app with mappings router."""
    app = FastAPI()
    app.include_router(router, prefix="/casbin_policies")

    # Mock permission check dependency
    async def mock_permission():
        pass

    app.dependency_overrides[policy_permission_required] = mock_permission
    return app


@pytest.fixture
async def client(app_with_mappings_router):
    """Create test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app_with_mappings_router), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_list_routes(client):
    """Test listing all routes."""
    response = await client.get("/casbin_policies/routes")
    assert response.status_code == 200
    data = response.json()
    assert "routes" in data
    assert isinstance(data["routes"], list)


@pytest.mark.asyncio
async def test_list_routes_excludes_docs(client):
    """Test that list_routes excludes documentation routes."""
    response = await client.get("/casbin_policies/routes")
    assert response.status_code == 200
    data = response.json()
    routes = data["routes"]
    assert "/docs" not in routes
    assert "/redoc" not in routes
    assert "/openapi.json" not in routes


@pytest.mark.asyncio
async def test_list_permission_mappings(client):
    """Test listing all permission mappings."""
    response = await client.get("/casbin_policies/permission_mappings")
    assert response.status_code == 200
    data = response.json()
    assert "mappings" in data
    assert isinstance(data["mappings"], list)


@pytest.mark.asyncio
async def test_create_permission_mapping(client):
    """Test creating a permission mapping."""
    mapping_data = {"api_name": "test_route", "permission": "test_permission"}
    response = await client.post("/casbin_policies/permission_mappings", json=mapping_data)
    assert response.status_code == 201
    data = response.json()
    assert data["api_name"] == "test_route"
    assert data["permission"] == "test_permission"


@pytest.mark.asyncio
async def test_create_duplicate_permission_mapping(client):
    """Test creating a duplicate permission mapping returns 400."""
    mapping_data = {"api_name": "duplicate_route", "permission": "duplicate_permission"}
    # Create first time
    await client.post("/casbin_policies/permission_mappings", json=mapping_data)
    # Try to create again
    response = await client.post("/casbin_policies/permission_mappings", json=mapping_data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_permission_mapping(client):
    """Test deleting a permission mapping."""
    # First create a mapping
    mapping_data = {"api_name": "delete_route", "permission": "delete_permission"}
    await client.post("/casbin_policies/permission_mappings", json=mapping_data)

    # Then delete it
    response = await client.request(
        "DELETE", "/casbin_policies/permission_mappings", json=mapping_data
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_nonexistent_permission_mapping(client):
    """Test deleting a non-existent permission mapping returns 404."""
    mapping_data = {"api_name": "nonexistent_route", "permission": "nonexistent_permission"}
    response = await client.request(
        "DELETE", "/casbin_policies/permission_mappings", json=mapping_data
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_permission_groups(client):
    """Test listing all permission groups."""
    # First create some mappings
    mapping1 = {"api_name": "route1", "permission": "perm1"}
    mapping2 = {"api_name": "route2", "permission": "perm1"}
    mapping3 = {"api_name": "route3", "permission": "perm2"}
    
    await client.post("/casbin_policies/permission_mappings", json=mapping1)
    await client.post("/casbin_policies/permission_mappings", json=mapping2)
    await client.post("/casbin_policies/permission_mappings", json=mapping3)

    response = await client.get("/casbin_policies/permission_groups")
    assert response.status_code == 200
    data = response.json()
    assert "groups" in data
    assert isinstance(data["groups"], list)
    
    # Check that groups are properly organized
    groups = {g["permission"]: g["api_names"] for g in data["groups"]}
    assert "perm1" in groups
    assert "perm2" in groups
    assert "route1" in groups["perm1"]
    assert "route2" in groups["perm1"]
    assert "route3" in groups["perm2"]


@pytest.mark.asyncio
async def test_update_permission_group(client):
    """Test updating a permission group."""
    # First create some mappings
    mapping1 = {"api_name": "old_route1", "permission": "update_perm"}
    mapping2 = {"api_name": "old_route2", "permission": "update_perm"}
    
    await client.post("/casbin_policies/permission_mappings", json=mapping1)
    await client.post("/casbin_policies/permission_mappings", json=mapping2)

    # Update the permission group
    update_data = {"api_names": ["new_route1", "new_route2"]}
    response = await client.put(
        "/casbin_policies/permission_groups/update_perm", json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["permission"] == "update_perm"
    assert set(data["api_names"]) == {"new_route1", "new_route2"}


@pytest.mark.asyncio
async def test_delete_permission_group(client):
    """Test deleting a permission group."""
    # First create some mappings
    mapping1 = {"api_name": "group_route1", "permission": "group_perm"}
    mapping2 = {"api_name": "group_route2", "permission": "group_perm"}
    
    await client.post("/casbin_policies/permission_mappings", json=mapping1)
    await client.post("/casbin_policies/permission_mappings", json=mapping2)

    # Delete the permission group
    response = await client.delete("/casbin_policies/permission_groups/group_perm")
    assert response.status_code == 204

    # Verify mappings are deleted
    mappings_response = await client.get("/casbin_policies/permission_mappings")
    mappings = mappings_response.json()["mappings"]
    group_mappings = [m for m in mappings if m.get("permission") == "group_perm"]
    assert len(group_mappings) == 0


@pytest.mark.asyncio
async def test_delete_nonexistent_permission_group(client):
    """Test deleting a non-existent permission group returns 404."""
    response = await client.delete("/casbin_policies/permission_groups/nonexistent_perm")
    assert response.status_code == 404

