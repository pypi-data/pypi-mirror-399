#!/usr/bin/python
# -*- coding: utf-8 -*-

from aiohttp.web import middleware, Request, StreamResponse
from rivista.utility.logger import UtilityLogger
from rivista.utility.text import UtilityText
import sys

logger = UtilityLogger(__name__)

class HttpMiddleware:

    from typing import Callable, Awaitable

    @middleware
    async def user_agent_check(
        request: Request,
        handler: Callable[[Request], Awaitable[StreamResponse]]
    ) -> StreamResponse:
        user_agent = request.message.headers["User-Agent"]
        is_included = UtilityText.is_included(
            ["Chrome", "Edg", "EdgA", "EdgiOS", "Firefox", "FxiOS", "OPR",
             "Safari", "Trident", "YaBrowser", "Yowser", "Vivaldi"],
            user_agent)
        if is_included: print(user_agent)
        # This affects SVG
        #resp = await handler(request)
        #resp.text = resp.text + ' wink'
        #return resp
        return await handler(request)

    @middleware
    async def operating_system_check(
        request: Request,
        handler: Callable[[Request], Awaitable[StreamResponse]]
    ) -> StreamResponse:
        user_agent = request.message.headers["User-Agent"]
        is_included = UtilityText.is_included(
            ["CrOS", "Fedora", "iPad", "iPhone", "iPod", "Mac OS", "Macintosh",
             "Ubuntu", "Windows"],
            user_agent)
        if is_included: print(user_agent)
        # This affects SVG
        #resp = await handler(request)
        #resp.text = resp.text + ' wink'
        #return resp
        return await handler(request)
