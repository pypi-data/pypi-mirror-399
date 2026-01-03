"""
API-Permission mapping router.

This module provides endpoints for managing API-Permission mappings (g2 rules).
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.routing import APIRoute

from ..utils import ensure_acl_initialized
from ..dependency import policy_permission_required
from ..schema import (
    PermissionApiMappingCreate,
    PermissionApiMappingResponse,
    PermissionApiMappingListResponse,
    RouteListResponse,
    PermissionGroupItem,
    PermissionGroupListResponse,
    PermissionGroupUpdate,
)
from ..enforcer import acl

router = APIRouter(tags=["Casbin Policy"])


@router.get(
    "/routes",
    response_model=RouteListResponse,
    name="casbin_policy_list_routes",
)
async def list_routes(
    request: Request,
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    List all registered route names (api_names).

    Returns all route names from the FastAPI application for use in permission mapping.
    """
    try:
        app = request.app
        routes = []
        for route in app.routes:
            if isinstance(route, APIRoute):
                # Skip documentation routes
                if route.path in ["/docs", "/redoc", "/openapi.json"]:
                    continue
                # Get route name (api_name)
                api_name = route.name
                if api_name:
                    routes.append(api_name)

        return RouteListResponse(routes=sorted(routes))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list routes: {str(e)}")


@router.get(
    "/permission_mappings",
    response_model=PermissionApiMappingListResponse,
    name="casbin_policy_list_permission_mappings",
)
async def list_permission_mappings(
    request: Request,
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    List all API-Permission mappings based on route table.

    Returns all routes from the route table with their permission mappings.
    Routes without mappings will have permission set to null.
    """
    try:
        app = request.app
        # Get all routes from the application
        route_names = set()
        for route in app.routes:
            if isinstance(route, APIRoute):
                if route.path in ["/docs", "/redoc", "/openapi.json"]:
                    continue
                api_name = route.name
                if api_name:
                    route_names.add(api_name)

        # Get all g2 mappings (api_name -> permission)
        mappings = acl.enforcer.get_named_grouping_policy("g2")
        permission_map = {m[0]: m[1] for m in mappings}  # api_name -> permission

        # Build response: include all routes, with permission if mapped
        mapping_list = []
        for api_name in sorted(route_names):
            permission = permission_map.get(api_name)
            mapping_list.append(
                PermissionApiMappingResponse(api_name=api_name, permission=permission)
            )

        return PermissionApiMappingListResponse(mappings=mapping_list)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list permission mappings: {str(e)}"
        )


@router.post(
    "/permission_mappings",
    response_model=PermissionApiMappingResponse,
    status_code=201,
    name="casbin_policy_create_permission_mapping",
)
async def create_permission_mapping(
    mapping: PermissionApiMappingCreate,
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Create an API-Permission mapping.

    Maps an API route name (api_name) to a permission using g2 rules.
    Format: "api_name" -> permission
    """
    try:
        # 使用 g2 添加 API -> Permission 映射
        # g2 key 就是 api_name
        added = await acl.enforcer.add_named_grouping_policy(
            "g2", mapping.api_name, mapping.permission
        )
        if not added:
            raise HTTPException(
                status_code=400,
                detail="Permission mapping already exists or failed to add",
            )
        # Notify all workers to reload policies
        await acl.notify_policy_update()
        return PermissionApiMappingResponse(
            api_name=mapping.api_name,
            permission=mapping.permission,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create permission mapping: {str(e)}"
        )


@router.delete(
    "/permission_mappings",
    status_code=204,
    name="casbin_policy_delete_permission_mapping",
)
async def delete_permission_mapping(
    mapping: PermissionApiMappingCreate,
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Delete an API-Permission mapping.

    Removes a g2 rule (api_name -> Permission mapping).
    """
    try:
        # g2 key 就是 api_name
        removed = await acl.enforcer.remove_named_grouping_policy(
            "g2", mapping.api_name, mapping.permission
        )
        if not removed:
            raise HTTPException(status_code=404, detail="Permission mapping not found")
        # Notify all workers to reload policies
        await acl.notify_policy_update()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete permission mapping: {str(e)}"
        )


@router.get(
    "/permission_groups",
    response_model=PermissionGroupListResponse,
    name="casbin_policy_list_permission_groups",
)
async def list_permission_groups(
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    List all permission groups.

    Returns all permissions grouped with their associated API route names.
    """
    try:
        # Get all g2 mappings (api_name -> permission)
        mappings = acl.enforcer.get_named_grouping_policy("g2")

        # Group by permission
        permission_groups: dict[str, list[str]] = {}
        for m in mappings:
            # m format: ["api_name", "permission"]
            api_name = m[0]
            permission = m[1]

            if permission not in permission_groups:
                permission_groups[permission] = []
            permission_groups[permission].append(api_name)

        # Convert to response format
        groups = [
            PermissionGroupItem(permission=perm, api_names=sorted(api_names))
            for perm, api_names in sorted(permission_groups.items())
        ]

        return PermissionGroupListResponse(groups=groups)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list permission groups: {str(e)}"
        )


@router.put(
    "/permission_groups/{permission}",
    response_model=PermissionGroupItem,
    name="casbin_policy_update_permission_group",
)
async def update_permission_group(
    permission: str,
    data: PermissionGroupUpdate,
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Update a permission group.

    Updates the API route names mapped to a specific permission.
    This will remove all existing mappings for the permission and add new ones.
    """
    try:
        enforcer = acl.enforcer

        # Get all existing mappings for this permission
        all_mappings = enforcer.get_named_grouping_policy("g2")
        existing_api_names = [m[0] for m in all_mappings if m[1] == permission]

        # Remove all existing mappings for this permission
        for api_name in existing_api_names:
            await enforcer.remove_named_grouping_policy("g2", api_name, permission)

        # Add new mappings
        for api_name in data.api_names:
            await enforcer.add_named_grouping_policy("g2", api_name, permission)

        # Save and notify
        await acl.save_policy()
        await acl.notify_policy_update()

        return PermissionGroupItem(
            permission=permission, api_names=sorted(data.api_names)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update permission group: {str(e)}"
        )


@router.delete(
    "/permission_groups/{permission}",
    status_code=204,
    name="casbin_policy_delete_permission_group",
)
async def delete_permission_group(
    permission: str,
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Delete a permission group.

    Removes all API route mappings for a specific permission.
    """
    try:
        enforcer = acl.enforcer

        # Get all existing mappings for this permission
        all_mappings = enforcer.get_named_grouping_policy("g2")
        existing_api_names = [m[0] for m in all_mappings if m[1] == permission]

        if not existing_api_names:
            raise HTTPException(
                status_code=404,
                detail=f"No mappings found for permission: {permission}",
            )

        # Remove all mappings for this permission
        for api_name in existing_api_names:
            await enforcer.remove_named_grouping_policy("g2", api_name, permission)

        # Save and notify
        await acl.save_policy()
        await acl.notify_policy_update()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete permission group: {str(e)}"
        )
