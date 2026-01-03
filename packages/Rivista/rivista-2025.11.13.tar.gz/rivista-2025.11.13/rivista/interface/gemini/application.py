#!/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio
from rivista.interface.gemini.ipc import GeminiIpc
from rivista.interface.gemini.task import GeminiTask
from rivista.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class GeminiApplication:

    async def initiate() -> None:
        asyncio.create_task(GeminiIpc.server())

