"""
Tests for fastapi_casbin_acl.enforcer module.
"""

import pytest
import os
import casbin
from fastapi_casbin_acl.enforcer import acl, AsyncEnforcerManager
from fastapi_casbin_acl.config import ACLConfig
from fastapi_casbin_acl.exceptions import ACLNotInitialized


@pytest.fixture
def reset_acl():
    """Reset ACL singleton state before and after test."""
    # Reset before
    acl._enforcers = {}
    acl._adapters = {}
    acl._config = None
    acl._initialized = False
    yield
    # Reset after
    acl._enforcers = {}
    acl._adapters = {}
    acl._config = None
    acl._initialized = False


@pytest.mark.asyncio
async def test_init_with_default_config(reset_acl):
    """Test init with default config creation."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)

    # Call init without config - should create default
    await acl.init(adapter=adapter)

    assert acl._config is not None
    assert acl._initialized is True


@pytest.mark.asyncio
async def test_get_enforcer_not_initialized(reset_acl):
    """Test get_enforcer raises ACLNotInitialized when model not initialized."""
    with pytest.raises(ACLNotInitialized, match="not initialized"):
        acl.get_enforcer("rbac")


@pytest.mark.asyncio
async def test_enforcer_property_not_initialized(reset_acl):
    """Test enforcer property raises ACLNotInitialized when not initialized."""
    with pytest.raises(ACLNotInitialized, match="not initialized"):
        _ = acl.enforcer


@pytest.mark.asyncio
async def test_config_property_not_initialized(reset_acl):
    """Test config property raises ACLNotInitialized when not initialized."""
    with pytest.raises(ACLNotInitialized, match="not initialized"):
        _ = acl.config


@pytest.mark.asyncio
async def test_load_policy(reset_acl):
    """Test load_policy method."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)
    config = ACLConfig()

    await acl.init(adapter=adapter, config=config)

    # Load policy should not raise
    await acl.load_policy()

    # Verify policies are loaded
    enforcer = acl.get_enforcer("permission_rbac")
    policies = enforcer.get_policy()
    assert len(policies) > 0


@pytest.mark.asyncio
async def test_load_policy_specific_model(reset_acl):
    """Test load_policy for a specific model."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)

    await acl.init(adapter=adapter, models=["permission_rbac", "abac"])

    # Load policy for specific model should not raise
    await acl.load_policy("permission_rbac")


@pytest.mark.asyncio
async def test_save_policy(reset_acl):
    """Test save_policy method."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)
    config = ACLConfig()

    await acl.init(adapter=adapter, config=config)

    # Save policy should not raise
    await acl.save_policy()


@pytest.mark.asyncio
async def test_enforce_rbac_model(reset_acl):
    """Test enforce method with RBAC model."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)

    await acl.init(adapter=adapter, models=["permission_rbac"])

    # Test enforce - RBAC model requires 3 args (sub, obj, act)
    assert acl.enforce("permission_rbac", "alice", "/public", "read") is True


@pytest.mark.asyncio
async def test_init_model_at_runtime(reset_acl):
    """Test init_model to add new model at runtime."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)

    # First init with ABAC only
    await acl.init(adapter=adapter, models=["abac"])
    assert not acl.is_model_initialized("permission_rbac")

    # Add RBAC at runtime
    await acl.init_model("permission_rbac")
    assert acl.is_model_initialized("permission_rbac")


@pytest.mark.asyncio
async def test_singleton_pattern(reset_acl):
    """Test that AsyncEnforcerManager is a singleton."""
    manager1 = AsyncEnforcerManager()
    manager2 = AsyncEnforcerManager()

    assert manager1 is manager2
    assert manager1 is acl


@pytest.mark.asyncio
async def test_init_with_external_model_path(reset_acl):
    """Test init with external_model_path in config."""
    import tempfile

    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)

    # Create a temporary external model file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False) as f:
        f.write("[request_definition]\nr = sub, obj, act\n")
        external_model_path = f.name

    try:
        config = ACLConfig()
        config.external_model_path = external_model_path

        await acl.init(adapter=adapter, config=config)

        # Check that external model is registered
        from fastapi_casbin_acl.registry import model_registry

        assert model_registry.is_registered("external")
    finally:
        if os.path.exists(external_model_path):
            os.unlink(external_model_path)


@pytest.mark.asyncio
async def test_init_with_app_parameter(reset_acl):
    """Test init with app parameter builds API name map."""
    from fastapi import FastAPI

    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)
    config = ACLConfig()

    app = FastAPI()

    @app.get("/test")
    async def test_route():
        return {"message": "ok"}

    await acl.init(adapter=adapter, config=config, app=app)

    # Check that API name map is built (no warning should be raised)
    assert acl._initialized is True


@pytest.mark.asyncio
async def test_init_with_policy_router_enabled(reset_acl):
    """Test init with policy router enabled and app provided."""
    from fastapi import FastAPI

    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)
    config = ACLConfig()
    config.policy_router_enable = True

    app = FastAPI()

    await acl.init(adapter=adapter, config=config, app=app)

    # Check that router is registered
    assert acl._initialized is True
    # Router should be included in app
    assert len([r for r in app.routes if "/casbin_policies" in str(r.path)]) > 0


@pytest.mark.asyncio
async def test_init_model_without_adapter(reset_acl):
    """Test init_model without adapter uses first available adapter."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)

    # First init with one model
    await acl.init(adapter=adapter, models=["permission_rbac"])

    # Add another model without adapter
    await acl.init_model("abac")

    assert acl.is_model_initialized("abac")


@pytest.mark.asyncio
async def test_init_model_without_adapter_no_initialized(reset_acl):
    """Test init_model without adapter raises error when no models initialized."""
    with pytest.raises(ACLNotInitialized, match="No adapter available"):
        await acl.init_model("permission_rbac")


@pytest.mark.asyncio
async def test_init_model_skip_already_initialized(reset_acl):
    """Test _init_model skips if model already initialized."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)

    await acl.init(adapter=adapter, models=["permission_rbac"])

    # Get the enforcer before
    enforcer_before = acl.get_enforcer("permission_rbac")

    # Try to init again (should skip)
    await acl._init_model("permission_rbac", adapter)

    # Should be the same enforcer instance
    enforcer_after = acl.get_enforcer("permission_rbac")
    assert enforcer_before is enforcer_after


@pytest.mark.asyncio
async def test_get_enforcer_with_available_models(reset_acl):
    """Test get_enforcer error message shows available models."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)

    await acl.init(adapter=adapter, models=["permission_rbac"])

    with pytest.raises(ACLNotInitialized) as exc_info:
        acl.get_enforcer("nonexistent")

    assert "Available models" in str(exc_info.value)
    assert "permission_rbac" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_enforcer_no_models_initialized(reset_acl):
    """Test get_enforcer error message when no models initialized."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)

    await acl.init(adapter=adapter, models=[])

    with pytest.raises(ACLNotInitialized) as exc_info:
        acl.get_enforcer("permission_rbac")

    assert "none" in str(exc_info.value).lower() or "Available models" in str(
        exc_info.value
    )


@pytest.mark.asyncio
async def test_enforcer_property_uses_default_model(reset_acl):
    """Test enforcer property returns default model enforcer."""
    policy_path = os.path.join(os.path.dirname(__file__), "policy.csv")
    adapter = casbin.persist.adapters.asyncio.AsyncFileAdapter(policy_path)

    await acl.init(adapter=adapter, models=["permission_rbac"])

    enforcer1 = acl.enforcer
    enforcer2 = acl.get_enforcer("permission_rbac")

    assert enforcer1 is enforcer2


@pytest.mark.asyncio
async def test_enforcer_property_not_initialized_config_none(reset_acl):
    """Test enforcer property raises error when config is None."""
    # Set initialized to True but config to None
    acl._initialized = True
    acl._config = None

    with pytest.raises(ACLNotInitialized):
        _ = acl.enforcer
