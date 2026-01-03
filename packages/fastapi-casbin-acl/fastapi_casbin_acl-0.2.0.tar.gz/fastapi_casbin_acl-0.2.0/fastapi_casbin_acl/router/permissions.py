"""
Permission management router.

This module provides endpoints for managing permissions.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Request

from ..utils import ensure_acl_initialized, resolve_subject
from ..dependency import policy_permission_required
from ..exceptions import Unauthorized
from ..schema import (
    PermissionCreate,
    PermissionResponse,
    PermissionListResponse,
    UserPermissionListResponse,
)
from ..enforcer import acl

router = APIRouter(prefix="/permissions", tags=["Casbin Policy"])


@router.get(
    "", response_model=PermissionListResponse, name="casbin_policy_list_permissions"
)
async def list_permissions(
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    List all permissions.

    Returns all unique permissions from policy rules (p).
    """
    try:
        # get all policies, extract unique permissions (obj)
        policies = acl.enforcer.get_policy()
        permissions = set([])
        for policy in policies:
            if len(policy) > 1:
                permissions.add((policy[1], policy[2]))  # obj is the permission

        permission_list = [
            PermissionResponse(name=perm[0], level=perm[1])
            for perm in sorted(permissions)
        ]
        return PermissionListResponse(permissions=permission_list)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list permissions: {str(e)}"
        )


@router.get(
    "/search",
    response_model=PermissionListResponse,
    name="casbin_policy_search_permissions",
)
async def search_permissions(
    q: Optional[str] = Query(
        None, description="Search query for permission name (fuzzy match)"
    ),
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Search permissions with fuzzy matching.

    Returns all permissions that match the search query (case-insensitive).
    If no query is provided, returns all permissions.
    """
    try:
        # Get all policies, extract unique permissions (obj)
        policies = acl.enforcer.get_policy()
        permissions = set()
        for policy in policies:
            if len(policy) > 1:
                permissions.add((policy[1], policy[2]))  # obj is the permission

        # Apply fuzzy search if query provided
        if q:
            q_lower = q.lower()
            permissions = {perm for perm in permissions if q_lower in perm[0].lower()}

        permission_list = [
            PermissionResponse(name=perm[0], level=perm[1])
            for perm in sorted(permissions)
        ]
        return PermissionListResponse(permissions=permission_list)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to search permissions: {str(e)}"
        )


@router.get(
    "/me",
    response_model=UserPermissionListResponse,
    name="casbin_policy_get_user_permissions",
)
async def get_user_permissions(
    request: Request,
    _init: None = Depends(ensure_acl_initialized),
):
    """
    Get current user's permissions.

    Returns all permission names that the current user has access to.
    This includes permissions granted directly to the user and through roles.
    """
    try:
        config = acl.config

        # Check if get_subject is configured
        if config.get_subject is None:
            raise HTTPException(
                status_code=500,
                detail="get_subject is not configured. Cannot determine current user.",
            )

        # Get current user
        sub = await resolve_subject(request, config.get_subject)
        if sub is None:
            raise Unauthorized("User not authenticated")

        sub_str = str(sub)
        enforcer = acl.enforcer

        # Get all roles for the user (g rules: g, user, role)
        roles = await enforcer.get_roles_for_user(sub_str)

        # Collect all subjects (user + roles)
        subjects = [sub_str]
        subjects.extend(roles)

        # Get all permissions for the user and their roles
        # In permission_rbac model, policies are: p, sub, obj, act
        # where obj is the permission name
        permission_set = set()

        # Get all policies
        policies = enforcer.get_policy()
        for policy in policies:
            if len(policy) >= 3:
                policy_sub = policy[0]  # subject (user or role)
                permission_obj = policy[1]  # permission name

                # If this policy applies to the user or one of their roles
                if policy_sub in subjects:
                    permission_set.add(permission_obj)

        return UserPermissionListResponse(permissions=sorted(list(permission_set)))
    except Unauthorized:
        raise
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get user permissions: {str(e)}"
        )
