#!/usr/bin/python
# -*- coding: utf-8 -*-

from rivista.publish.xhtml import PublishXhtml
from rivista.publish.xml import PublishXml
import asyncio
import sys

class HttpTask:

    async def looper(account):
        function_name = sys._getframe().f_code.co_name
        #logger.debug(f"{function_name}	{account}	Start")
        while True:
            await PublishXhtml.content(account)
            await PublishXml.content(account)
            await asyncio.sleep(60 * 120)

    def restart_task(account):
        function_name = sys._getframe().f_code.co_name
        #logger.debug(f"{function_name}	{account}	Start")
        config_account = accounts.retrieve(account)
        UtilityTask.stop(config_account.tasks_manager, "publish")
        config_account.tasks_manager["publish"] = asyncio.create_task(
            HttpTask.looper(account))
        #logger.debug(f"{function_name}	{account}	Finish")
