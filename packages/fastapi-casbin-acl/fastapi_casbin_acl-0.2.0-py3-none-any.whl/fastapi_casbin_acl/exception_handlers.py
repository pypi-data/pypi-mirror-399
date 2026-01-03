#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: harumonia
@Email: zxjlm233@gmail.net
@Create Time: 2025-12-29 15:29:22
@Software: Visual Studio Code
@Copyright: Copyright (c) 2025, harumonia
@Description: Exception handlers for fastapi-casbin-acl
All Rights Reserved.
"""
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.responses import Response

from fastapi_casbin_acl.exceptions import Unauthorized, Forbidden


async def unauthorized_handler(request: Request, exc: Unauthorized) -> Response:
    """
    Unauthorized exception handler

    when the user is not authenticated (subject is None/missing) but permission is required

    Args:
        request: FastAPI request object
        exc: Unauthorized exception instance

    Returns:
        JSONResponse: return 401 status code and error message
    """
    return JSONResponse(
        status_code=401,
        content={
            "message": "Unauthorized: please provide valid user authentication information",
            "detail": "User not authenticated or authentication information missing, cannot access protected resources",
        },
    )


async def forbidden_handler(request: Request, exc: Forbidden) -> Response:
    """
    Forbidden exception handler

    when the user is authenticated but lacks the required permission

    Args:
        request: FastAPI request object
        exc: Forbidden exception instance

    Returns:
        JSONResponse: return 403 status code and error message
    """
    return JSONResponse(
        status_code=403,
        content={
            "message": "Forbidden: you do not have permission to execute this operation",
            "detail": "User authenticated, but lacks the required permission to access the resource",
        },
    )
