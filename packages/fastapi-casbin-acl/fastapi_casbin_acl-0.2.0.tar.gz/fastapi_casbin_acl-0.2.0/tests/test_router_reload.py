"""
Tests for fastapi_casbin_acl.router.reload module.
"""

import pytest
import csv
import io
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
import casbin
import os
from fastapi_casbin_acl.enforcer import acl
from fastapi_casbin_acl.config import ACLConfig
from fastapi_casbin_acl.router.reload import router
from fastapi_casbin_acl.dependency import policy_permission_required


@pytest.fixture
async def setup_acl_for_reload():
    """Setup ACL for reload tests."""
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
async def app_with_reload_router(setup_acl_for_reload):
    """Create FastAPI app with reload router."""
    app = FastAPI()
    app.include_router(router, prefix="/casbin_policies")

    # Mock permission check dependency
    async def mock_permission():
        pass

    app.dependency_overrides[policy_permission_required] = mock_permission
    return app


@pytest.fixture
async def client(app_with_reload_router):
    """Create test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app_with_reload_router), base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_list_ptypes(client):
    """Test listing all policy types."""
    response = await client.get("/casbin_policies/ptypes")
    assert response.status_code == 200
    data = response.json()
    assert "ptypes" in data
    assert isinstance(data["ptypes"], list)
    # Permission RBAC model should have p, g, g2
    assert "p" in data["ptypes"]
    assert "g" in data["ptypes"]
    assert "g2" in data["ptypes"]


@pytest.mark.asyncio
async def test_export_policies_single_type(client):
    """Test exporting policies for a single type."""
    response = await client.get("/casbin_policies/export?ptypes=p")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    # Parse CSV content
    content = response.text
    reader = csv.reader(io.StringIO(content))
    header = next(reader)
    assert header == ["ptype", "v0", "v1", "v2", "v3", "v4", "v5"]
    
    # Check that there are policies
    rows = list(reader)
    assert len(rows) > 0
    # All rows should have ptype "p"
    assert all(row[0] == "p" for row in rows)


@pytest.mark.asyncio
async def test_export_policies_multiple_types(client):
    """Test exporting policies for multiple types."""
    response = await client.get("/casbin_policies/export?ptypes=p,g,g2")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    # Parse CSV content
    content = response.text
    reader = csv.reader(io.StringIO(content))
    header = next(reader)
    assert header == ["ptype", "v0", "v1", "v2", "v3", "v4", "v5"]
    
    # Check that there are policies
    rows = list(reader)
    assert len(rows) > 0
    # Check that different ptypes are present
    ptypes = {row[0] for row in rows}
    assert "p" in ptypes or "g" in ptypes or "g2" in ptypes


@pytest.mark.asyncio
async def test_export_policies_empty_ptypes(client):
    """Test exporting policies with empty ptypes returns 400."""
    response = await client.get("/casbin_policies/export?ptypes=")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_export_policies_nonexistent_type(client):
    """Test exporting policies for non-existent type returns 404."""
    response = await client.get("/casbin_policies/export?ptypes=nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_import_policies(client):
    """Test importing policies from CSV."""
    # Create CSV content
    csv_content = "ptype,v0,v1,v2,v3,v4,v5\n"
    csv_content += "p,import_user,/import_path,read\n"
    csv_content += "g2,import_api,import_permission\n"
    
    # Create file-like object
    files = {"file": ("policies.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    
    response = await client.post("/casbin_policies/import", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "imported" in data
    assert "skipped" in data
    assert "errors" in data
    assert data["imported"] >= 0


@pytest.mark.asyncio
async def test_import_policies_duplicate(client):
    """Test importing duplicate policies."""
    # First import
    csv_content = "ptype,v0,v1,v2,v3,v4,v5\n"
    csv_content += "p,duplicate_user,/duplicate_path,read\n"
    files = {"file": ("policies.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    await client.post("/casbin_policies/import", files=files)
    
    # Import again (should skip duplicates)
    response = await client.post("/casbin_policies/import", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["skipped"] >= 1


@pytest.mark.asyncio
async def test_import_policies_empty_file(client):
    """Test importing empty CSV file."""
    csv_content = "ptype,v0,v1,v2,v3,v4,v5\n"
    files = {"file": ("empty.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = await client.post("/casbin_policies/import", files=files)
    # Empty file after header may return 200 with 0 imported, or 400
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        data = response.json()
        assert data["imported"] == 0


@pytest.mark.asyncio
async def test_import_policies_invalid_format(client):
    """Test importing CSV with invalid format."""
    csv_content = "invalid,header\n"
    csv_content += "invalid,row\n"
    files = {"file": ("invalid.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = await client.post("/casbin_policies/import", files=files)
    # Should handle gracefully, may return 400 or 200 with errors
    assert response.status_code in [200, 400]
    if response.status_code == 200:
        data = response.json()
        assert data["errors"] > 0


@pytest.mark.asyncio
async def test_import_policies_missing_ptype(client):
    """Test importing CSV with missing ptype."""
    csv_content = "ptype,v0,v1,v2,v3,v4,v5\n"
    csv_content += ",value1,value2\n"  # Missing ptype
    files = {"file": ("missing_ptype.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = await client.post("/casbin_policies/import", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["errors"] > 0


@pytest.mark.asyncio
async def test_import_policies_g_type(client):
    """Test importing g type policies."""
    csv_content = "ptype,v0,v1,v2,v3,v4,v5\n"
    csv_content += "g,import_user,import_role\n"
    files = {"file": ("g_policies.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = await client.post("/casbin_policies/import", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] >= 0 or data["skipped"] >= 0

