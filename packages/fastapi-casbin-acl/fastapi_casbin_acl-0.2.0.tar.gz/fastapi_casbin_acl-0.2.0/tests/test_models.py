"""
Tests for fastapi_casbin_acl.models module.
"""

import pytest
import os
from fastapi_casbin_acl.models import get_model_path, list_builtin_models


def test_get_model_path_abac():
    """Test get_model_path for ABAC model."""
    path = get_model_path("abac")
    assert os.path.exists(path)
    assert path.endswith("abac.conf")


def test_list_builtin_models():
    """Test list_builtin_models returns expected models."""
    models = list_builtin_models()
    assert "rbac" in models
    assert "abac" in models


def test_get_model_path_file_not_found(monkeypatch):
    """Test get_model_path raises FileNotFoundError when file doesn't exist."""

    # Mock os.path.exists to return False
    def mock_exists(path):
        if path.endswith(".conf"):
            return False
        return True

    monkeypatch.setattr("os.path.exists", mock_exists)

    # Should raise FileNotFoundError
    with pytest.raises(FileNotFoundError, match="Casbin model file not found"):
        get_model_path("rbac")
