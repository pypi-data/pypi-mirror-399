#!/usr/bin/python
# -*- coding: utf-8 -*-

from aiohttp.web import Application
import asyncio
from rivista.interface.http.ipc import HttpIpc
from rivista.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class HttpApplication:

    async def initiate(app: Application) -> None:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        # TODO Start task scan (scan for updates)
        # TODO Start task template (create static templates, instead of creating them upon request)
        #UtilitySubscriptionTask.restart_task("slixfeed")
        #HttpTask.restart_task("slixfeed")
        asyncio.create_task(HttpIpc.server())
