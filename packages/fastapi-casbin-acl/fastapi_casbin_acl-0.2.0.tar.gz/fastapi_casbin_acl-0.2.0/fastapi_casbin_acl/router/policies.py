"""
Policy CRUD operations router.

This module provides endpoints for managing Casbin policies (p rules).
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query

from ..utils import ensure_acl_initialized
from ..dependency import policy_permission_required
from ..schema import (
    PolicyPaginationResponse,
    PolicyResponse,
    PolicyListResponse,
    PolicyCreate,
)
from ..enforcer import acl

router = APIRouter(tags=["Casbin Policy"])


@router.get("", response_model=PolicyListResponse, name="casbin_policy_list_policies")
async def list_policies(
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    List all policies.

    Returns all policy rules (p) from the Casbin model.
    """
    try:
        policies = acl.enforcer.get_policy()
        policy_list = [PolicyResponse(sub=p[0], obj=p[1], act=p[2]) for p in policies]
        return PolicyListResponse(policies=policy_list)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list policies: {str(e)}"
        )


@router.post("", response_model=PolicyResponse, status_code=201, name="create_policy")
async def create_policy(
    policy: PolicyCreate,
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Create a new policy.

    Adds a policy rule to the Casbin model.
    """
    try:
        # add policy using async method
        added = await acl.enforcer.add_policy(policy.sub, policy.obj, policy.act)
        if not added:
            raise HTTPException(
                status_code=400, detail="Policy already exists or failed to add"
            )
        # Notify all workers to reload policies
        await acl.notify_policy_update()
        return PolicyResponse(sub=policy.sub, obj=policy.obj, act=policy.act)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to create policy: {str(e)}"
        )


@router.delete("", status_code=204, name="delete_policy")
async def delete_policy(
    policy: PolicyCreate,
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Delete a policy.

    Removes a policy rule from the Casbin model.
    """
    try:
        removed = await acl.enforcer.remove_policy(policy.sub, policy.obj, policy.act)
        if not removed:
            raise HTTPException(status_code=404, detail="Policy not found")
        # Notify all workers to reload policies
        await acl.notify_policy_update()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete policy: {str(e)}"
        )


@router.get(
    "/list",
    response_model=PolicyPaginationResponse,
    name="casbin_policy_paginate_policies",
)
async def paginate_policies(
    current_page: int = Query(1, ge=1, description="current page"),
    limit: int = Query(10, ge=1, le=100, description="limit per page"),
    sub: Optional[str] = Query(None, description="filter subject"),
    obj: Optional[str] = Query(None, description="filter object"),
    act: Optional[str] = Query(None, description="filter action"),
    _init: None = Depends(ensure_acl_initialized),
    _perm: None = Depends(policy_permission_required),
):
    """
    Paginate policies.

    :param current_page: current page
    :param limit: limit per page
    :param sub: filter subject
    :param obj: filter object
    :param act: filter action
    :return: paginated policies
    """
    try:
        # get all policies
        policies = acl.enforcer.get_policy()

        # convert to PolicyItem list
        policy_list = [PolicyResponse(sub=p[0], obj=p[1], act=p[2]) for p in policies]

        # apply filters
        if sub:
            policy_list = [p for p in policy_list if sub.lower() in p.sub.lower()]
        if obj:
            policy_list = [p for p in policy_list if obj.lower() in p.obj.lower()]
        if act:
            policy_list = [p for p in policy_list if act.lower() in p.act.lower()]

        # paginate
        total = len(policy_list)
        skip = (current_page - 1) * limit
        paginated_list = policy_list[skip : skip + limit]

        return PolicyPaginationResponse(
            total=total,
            current_page=current_page,
            limit=limit,
            list=paginated_list,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to list policies: {str(e)}"
        )
