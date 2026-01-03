"""
FastAPI dependency for permission checking.

This module provides the permission_required dependency factory that integrates
Casbin permission checking into FastAPI routes.
"""

from typing import Callable, Any

from fastapi import Request, Depends
from fastapi.routing import APIRoute

from .enforcer import acl
from .exceptions import ACLNotInitialized, Forbidden, Unauthorized
from .utils import resolve_subject


def permission_required(
    *,
    get_subject: Callable[..., Any],
    action: str = "",
) -> Callable:
    """
    Factory for the permission dependency using Permission RBAC model.

    This function uses the Permission RBAC model, which maps API paths to permissions
    via g2 rules, and then checks if the user's role has the required permission.

    :param get_subject: Callable dependency that returns the subject (user ID/username).
    :param action: The action being performed (e.g. "read", "write", "delete").

    Example:
        @app.get("/users")
        async def list_users(
            _: None = Depends(permission_required(
                get_subject=get_user,
                action="read"
            ))
        ):
            ...

        @app.post("/orders")
        async def create_order(
            _: None = Depends(permission_required(
                get_subject=get_user,
                action="write"
            ))
        ):
            ...
    """

    async def _dependency(request: Request, sub: str = Depends(get_subject)):
        # 1. Check Authentication
        if sub is None:
            raise Unauthorized("User not authenticated")

        # Ensure subject is a string for Casbin
        sub_str = str(sub)

        # 2. Get the route and extract api_name
        route = request.scope.get("route")
        if not route or not isinstance(route, APIRoute):
            raise Forbidden("Unable to determine route for permission check")

        api_name = route.name
        if not api_name:
            raise Forbidden("Route has no name, cannot perform permission check")

        # 3. Get the model from config (should be permission_rbac)
        model = "permission_rbac"

        # 4. Resolve Permission from api_name using g2 mappings
        # g2 format: "api_name" -> permission
        enforcer = acl.get_enforcer(model)
        mappings = enforcer.get_named_grouping_policy("g2")

        # Direct lookup: find mapping where api_key == api_name
        permission_obj = None
        for mapping in mappings:
            # mapping format: ["api_name", "permission"]
            api_key = mapping[0]
            permission = mapping[1]

            if api_key == api_name:
                permission_obj = permission
                break

        if permission_obj is None:
            # If no mapping found, raise Forbidden
            raise Forbidden(f"No permission mapping found for api_name: {api_name}")

        # 5. Enforce Policy
        # Permission RBAC model: use permission instead of obj
        if not acl.enforce(model, sub_str, permission_obj, action):
            raise Forbidden("Permission denied")

    return _dependency


def _get_policy_permission_dependency():
    """
    Return the permission check dependency for the policy router.

    :return: The permission check dependency function
    """

    async def _check_policy_permission(request: Request):
        """
        Check if the current user has permission to access the policy router.

        :param request: FastAPI Request object
        :raises Forbidden: If the permission check fails
        :raises Unauthorized: If the user is not authenticated
        """
        try:
            config = acl.config
        except ACLNotInitialized:
            # if ACL is not initialized, handle by ensure_acl_initialized
            return

        # if protection is not enabled, pass
        if not config.policy_router_enable:
            return

        # get get_subject function
        if config.get_subject is None:
            raise Forbidden(
                "Policy router protection enabled but get_subject not configured"
            )

        # call get_subject to get the current user (support Depends mechanism)
        sub = await resolve_subject(request, config.get_subject)

        if sub is None:
            raise Unauthorized("User not authenticated")

        allowed = acl.enforce("permission_rbac", str(sub), "policy_management", "write")

        if not allowed:
            raise Forbidden("Permission denied for policy management")

    return _check_policy_permission


# create permission check dependency
policy_permission_required = _get_policy_permission_dependency()
