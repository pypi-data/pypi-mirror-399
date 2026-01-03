"""
Role management router.

This module provides endpoints for managing roles and role bindings (g rules).
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from ..utils import ensure_acl_initialized
from ..dependency import policy_permission_required
from ..schema import (
    RoleBindingResponse,
    RoleListResponse,
    RoleBindingListResponse,
    RoleBindingCreate,
    RoleCreate,
)
from ..enforcer import acl

router = APIRouter(tags=["Casbin Policy"])


@router.post(
    "/roles",
    response_model=RoleBindingResponse,
    status_code=201,
    name="casbin_policy_create_role_binding",
)
async def create_role_binding(
    binding: RoleBindingCreate,
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Create a role binding.

    Assigns a role to a user.
    """
    try:
        added = await acl.enforcer.add_role_for_user(binding.user, binding.role)
        if not added:
            raise HTTPException(
                status_code=400, detail="Role binding already exists or failed to add"
            )
        # Notify all workers to reload policies
        await acl.notify_policy_update()
        return RoleBindingResponse(user=binding.user, role=binding.role)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create role binding: {str(e)}"
        )


@router.delete("/roles", status_code=204, name="casbin_policy_delete_role_binding")
async def delete_role_binding(
    binding: RoleBindingCreate,
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Delete a role binding.

    Removes a role assignment from a user.
    """
    try:
        removed = await acl.enforcer.delete_role_for_user(binding.user, binding.role)
        if not removed:
            raise HTTPException(status_code=404, detail="Role binding not found")
        # Notify all workers to reload policies
        await acl.notify_policy_update()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete role binding: {str(e)}"
        )


@router.get("/roles", response_model=RoleListResponse, name="casbin_policy_list_roles")
async def list_roles(
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Get all roles list

    :return: roles list
    """
    try:
        # get all policies
        policies = acl.enforcer.get_policy()

        # extract all unique roles (subjects may be roles)
        roles = set()
        for policy in policies:
            sub = policy[0]
            # assume role is subject, can be determined by other ways
            # here we simply treat all subjects as possible roles
            roles.add(sub)

        # get all roles defined by get_roles_for_user
        # since there is no direct method to get all roles, we need to iterate through all users
        # here we simplify the processing, return all unique subjects

        return RoleListResponse(roles=list(sorted(roles)) if roles else [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list roles: {str(e)}")


@router.get(
    "/role_bindings",
    response_model=RoleBindingListResponse,
    name="casbin_policy_list_role_bindings",
)
async def list_role_bindings(
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Get all role bindings list

    :return: role bindings list
    """
    try:
        # get all role bindings (through g policy)
        role_bindings = acl.enforcer.get_grouping_policy()

        # convert to RoleBindingItem list
        binding_list = [
            RoleBindingResponse(user=rb[0], role=rb[1]) for rb in role_bindings
        ]

        return RoleBindingListResponse(list=binding_list)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list role bindings: {str(e)}"
        )


@router.get(
    "/roles/search",
    response_model=RoleListResponse,
    name="casbin_policy_search_roles",
)
async def search_roles(
    q: Optional[str] = Query(
        None, description="Search query for role name (fuzzy match)"
    ),
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Search roles with fuzzy matching.

    Returns all roles that match the search query (case-insensitive).
    If no query is provided, returns all roles.
    """
    try:
        # Get all policies
        policies = acl.enforcer.get_policy()

        # Extract all unique roles (subjects may be roles)
        roles = set()
        for policy in policies:
            sub = policy[0]
            roles.add(sub)

        # Get all roles from role bindings
        role_bindings = acl.enforcer.get_grouping_policy()
        for rb in role_bindings:
            roles.add(rb[1])  # role is the second element

        # Apply fuzzy search if query provided
        if q:
            q_lower = q.lower()
            roles = {role for role in roles if q_lower in role.lower()}

        return RoleListResponse(roles=list(sorted(roles)) if roles else [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search roles: {str(e)}")


@router.get(
    "/roles/{user}",
    response_model=RoleListResponse,
    name="casbin_policy_get_user_roles",
)
async def get_user_roles(
    user: str,
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Get all roles for a user.

    Returns the list of roles assigned to the specified user.
    """
    try:
        roles = await acl.enforcer.get_roles_for_user(user)
        return RoleListResponse(roles=roles if roles else [])
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get user roles: {str(e)}"
        )
