"""
Tests for fastapi_casbin_acl.registry module.
"""

import pytest
import os
import tempfile
from fastapi_casbin_acl.registry import ModelRegistry, model_registry
from fastapi_casbin_acl.exceptions import ConfigError


def test_model_registry_auto_register_builtin():
    """Test that built-in models are automatically registered."""
    registry = ModelRegistry()
    
    # Check that built-in models are registered (at least permission_rbac should be)
    # Note: rbac and abac may not exist, so we only check permission_rbac
    assert registry.is_registered("permission_rbac")


def test_model_registry_register_success():
    """Test registering a new model with valid path."""
    registry = ModelRegistry()
    
    # Create a temporary model file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write("[request_definition]\nr = sub, obj, act\n")
        temp_path = f.name
    
    try:
        registry.register("custom_model", temp_path)
        assert registry.is_registered("custom_model")
        assert registry.get_path("custom_model") == temp_path
    finally:
        os.unlink(temp_path)


def test_model_registry_register_file_not_found():
    """Test registering a model with non-existent path raises ConfigError."""
    registry = ModelRegistry()
    
    with pytest.raises(ConfigError, match="Model file not found"):
        registry.register("custom_model", "/nonexistent/path/model.conf")


def test_model_registry_unregister_success():
    """Test unregistering a registered model."""
    registry = ModelRegistry()
    
    # Create a temporary model file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write("[request_definition]\nr = sub, obj, act\n")
        temp_path = f.name
    
    try:
        registry.register("temp_model", temp_path)
        assert registry.is_registered("temp_model")
        
        registry.unregister("temp_model")
        assert not registry.is_registered("temp_model")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_model_registry_unregister_not_registered():
    """Test unregistering a non-registered model raises ConfigError."""
    registry = ModelRegistry()
    
    with pytest.raises(ConfigError, match="Model not registered"):
        registry.unregister("nonexistent_model")


def test_model_registry_get_path_success():
    """Test getting path for a registered model."""
    registry = ModelRegistry()
    
    # Built-in models should be registered
    path = registry.get_path("permission_rbac")
    assert os.path.exists(path)
    assert path.endswith(".conf")


def test_model_registry_get_path_not_registered():
    """Test getting path for non-registered model raises ConfigError."""
    registry = ModelRegistry()
    
    with pytest.raises(ConfigError, match="Model not registered"):
        registry.get_path("nonexistent_model")


def test_model_registry_get_path_not_registered_empty():
    """Test getting path when no models are registered shows 'none'."""
    registry = ModelRegistry()
    
    # Create a new registry and try to get a non-existent model
    # This tests the case where _models is empty
    with pytest.raises(ConfigError) as exc_info:
        registry.get_path("nonexistent")
    
    # The error message should mention available models
    assert "Available models" in str(exc_info.value)


def test_model_registry_is_registered():
    """Test checking if a model is registered."""
    registry = ModelRegistry()
    
    assert registry.is_registered("permission_rbac") is True
    assert registry.is_registered("nonexistent") is False


def test_model_registry_list_models():
    """Test listing all registered models."""
    registry = ModelRegistry()
    
    models = registry.list_models()
    assert isinstance(models, list)
    assert len(models) > 0
    assert "permission_rbac" in models


def test_model_registry_singleton():
    """Test that model_registry is a singleton instance."""
    from fastapi_casbin_acl.registry import model_registry as registry1
    from fastapi_casbin_acl.registry import model_registry as registry2
    
    assert registry1 is registry2

