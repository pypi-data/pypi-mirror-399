#!/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio
from rivista.publish.gmi import PublishGmi
from rivista.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class GeminiTask:

    async def looper(account):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        while True:
            await PublishGmi.content(account)
            await asyncio.sleep(60 * 120)

    def restart_task(account):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{account}	Start")
        config_account = accounts.retrieve(account)
        UtilityTask.stop(config_account.tasks_manager, "publish")
        config_account.tasks_manager["publish"] = asyncio.create_task(
            GeminiTask.looper(account))
        logger.debug(f"{function_name}	{account}	Finish")
