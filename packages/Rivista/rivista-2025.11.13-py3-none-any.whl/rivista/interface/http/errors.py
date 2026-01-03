#!/usr/bin/python
# -*- coding: utf-8 -*-

from aiohttp.web import (
    HTTPException,
    HTTPFound,
    Response,
    middleware)
from rivista.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class HttpErrors:

    async def handle_404(request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        return Response(
            text="404",
            content_type="text/plain")
    
    async def handle_500(request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        raw_path = request.raw_path
        if raw_path.endswith('/'):
            return Response(
                text="500",
                content_type="text/plain")
        else:
            #raise HTTPFound(raw_path + "/")
            raise HTTPFound(f"{raw_path}/")
    
    def create_error_middleware(overrides):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
    
        @middleware
        async def error_middleware(request, handler):
            try:
                return await handler(request)
            except HTTPException as ex:
                override = overrides.get(ex.status)
                if override:
                    return await override(request)
    
                raise
            except Exception:
                request.protocol.logger.exception("Error handling request")
                return await overrides[500](request)
    
        return error_middleware
    
    def setup_middlewares(app):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        error_middleware = HttpErrors.create_error_middleware({
            404: HttpErrors.handle_404,
            500: HttpErrors.handle_500
        })
        app.middlewares.append(error_middleware)
