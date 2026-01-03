#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: harumonia
@Email: zxjlm233@gmail.net
@Create Time: 2025-12-26 09:52:23
@Software: Visual Studio Code
@Copyright: Copyright (c) 2025, harumonia
@Description: ...
All Rights Reserved.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# Request/Response models
class PolicyCreate(BaseModel):
    """Request model for creating a policy."""

    sub: str = Field(..., description="Subject (user or role)")
    obj: str = Field(..., description="Object (resource path)")
    act: str = Field(
        default="multiple", description="Action (e.g., read, write, delete)"
    )


class PolicyResponse(BaseModel):
    """Response model for a policy."""

    sub: str
    obj: str
    act: str


class RoleBindingCreate(BaseModel):
    """Request model for creating a role binding."""

    user: str = Field(..., description="User identifier")
    role: str = Field(..., description="Role name")


class RoleBindingResponse(BaseModel):
    """Response model for a role binding."""

    user: str
    role: str


class PolicyListResponse(BaseModel):
    """Response model for listing policies."""

    policies: List[PolicyResponse]


class RoleListResponse(BaseModel):
    """Response model for listing roles."""

    roles: List[str]


class RoleCreate(BaseModel):
    """Request model for creating a role."""

    role: str = Field(..., description="Role name")


class PolicyPaginationResponse(BaseModel):
    """Response model for pagination."""

    total: int
    current_page: int
    limit: int
    list: List[PolicyResponse]


class RoleBindingListResponse(BaseModel):
    """Response model for pagination."""

    list: List[RoleBindingResponse]


# Permission models
class PermissionCreate(BaseModel):
    """Request model for creating a permission."""

    name: str = Field(..., description="Permission name")
    level: str = Field(default="read", description="Permission level")


class PermissionResponse(BaseModel):
    """Response model for a permission."""

    name: str
    level: str


class PermissionListResponse(BaseModel):
    """Response model for listing permissions."""

    permissions: List[PermissionResponse]


class UserPermissionListResponse(BaseModel):
    """Response model for listing current user's permissions."""

    permissions: List[str] = Field(
        ..., description="List of permission names the user has access to"
    )


# API-Permission mapping models
class PermissionApiMappingCreate(BaseModel):
    """Request model for creating an API-Permission mapping."""

    api_name: str = Field(..., description="API route name (from route.name attribute)")
    permission: str = Field(..., description="Permission name")


class PermissionApiMappingResponse(BaseModel):
    """Response model for an API-Permission mapping."""

    api_name: str
    permission: Optional[str] = Field(
        None, description="Permission name, null if not mapped"
    )


class PermissionApiMappingListResponse(BaseModel):
    """Response model for listing API-Permission mappings."""

    mappings: List[PermissionApiMappingResponse]


# Route list models
class RouteListResponse(BaseModel):
    """Response model for listing routes."""

    routes: List[str]


# Permission group models
class PermissionGroupItem(BaseModel):
    """Response model for a permission group."""

    permission: str = Field(..., description="Permission name")
    api_names: List[str] = Field(
        ..., description="List of API route names mapped to this permission"
    )


class PermissionGroupListResponse(BaseModel):
    """Response model for listing permission groups."""

    groups: List[PermissionGroupItem]


class PermissionGroupUpdate(BaseModel):
    """Request model for updating a permission group."""

    api_names: List[str] = Field(
        ..., description="List of API route names to map to the permission"
    )


# Policy explanation models
class PolicyExplainResponse(BaseModel):
    """Response model for policy explanation."""

    subject: str
    uri: str
    role_chain: List[str] = Field(..., description="Role chain from subject to roles")
    permission_mapping: Optional[str] = Field(
        None, description="Permission mapped to the URI"
    )
    matched_policies: List[PolicyResponse] = Field(
        ..., description="Matched policy rules"
    )
