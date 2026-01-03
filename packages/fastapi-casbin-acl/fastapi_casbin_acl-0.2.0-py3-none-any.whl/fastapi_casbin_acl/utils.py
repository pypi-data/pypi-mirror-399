#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: harumonia
@Email: zxjlm233@gmail.net
@Create Time: 2025-12-26 10:15:58
@Software: Visual Studio Code
@Copyright: Copyright (c) 2025, harumonia
@Description: ...
All Rights Reserved.
"""

from .enforcer import acl
from .exceptions import ACLNotInitialized
from fastapi import HTTPException, Request
from typing import Callable, Any, Optional
import inspect


def ensure_acl_initialized():
    """Dependency to ensure ACL is initialized."""
    try:
        _ = acl.config
        _ = acl.enforcer
    except ACLNotInitialized:
        raise HTTPException(
            status_code=500,
            detail="ACL system is not initialized. Call await acl.init() first.",
        )


async def resolve_subject(
    request: Request, get_subject: Callable[..., Any]
) -> Optional[str]:
    """
    Resolve subject, support FastAPI Depends mechanism.

    :param request: FastAPI Request object
    :param get_subject: The function to get the subject, it may be a dependency function
    :return: subject string, if cannot get, return None
    """
    try:
        # try to call get_subject directly
        # if get_subject accepts request parameter, pass request
        sig = inspect.signature(get_subject)
        params = list(sig.parameters.keys())

        if "request" in params:
            result = get_subject(request)
        elif len(params) == 0:
            result = get_subject()
        else:
            # try to pass request as the first parameter
            result = get_subject(request)

        # if the result is awaitable, wait
        if inspect.isawaitable(result):
            result = await result

        # if the result is None, return None
        if result is None:
            return None

        # convert to string
        return str(result)
    except Exception:
        # if the call fails, return None
        return None
