"""
Optional FastAPI router for Casbin policy management.
"""

from fastapi import APIRouter

from .policies import router as policies_router
from .roles import router as roles_router
from .permissions import router as permissions_router
from .mappings import router as mappings_router
from .reload import router as reload_router

# 创建主 router
# Note: prefix is not set in the router definition, but through the parameter in include_router
# This allows the prefix to be dynamically set through configuration
casbin_router = APIRouter(tags=["Casbin Policy"])

# 包含所有子路由
casbin_router.include_router(policies_router, prefix="/policy")
casbin_router.include_router(roles_router)
casbin_router.include_router(permissions_router)
casbin_router.include_router(mappings_router)
casbin_router.include_router(reload_router)

__all__ = ["casbin_router"]
