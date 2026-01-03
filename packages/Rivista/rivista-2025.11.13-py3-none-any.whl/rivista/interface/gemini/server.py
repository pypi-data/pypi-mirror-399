#!/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio
from jetforce import GeminiServer
import os
from rivista.interface.gemini.application import GeminiApplication
from rivista.interface.gemini.routes import routes
from rivista.property.publish import publish_properties
from rivista.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class InterfaceGeminiServer:

    def __init__(self):
        asyncio.run(GeminiApplication.initiate())
        settings = publish_properties.settings["server"]["gemini"]
        host = settings["host"]
        port = settings["port"]
        hostname = settings["hostname"]
        certfile = settings["certfile"] if settings["certfile"] else None
        keyfile = settings["keyfile"] if settings["keyfile"] else None
        server = GeminiServer(routes, host=host, port=port, hostname=hostname,
                              certfile=certfile, keyfile=keyfile)
        server.run()

        #asyncio.run(GeminiApplication.initiate())
        #asyncio.create_task(GeminiIpc.server())

        # Mount static graphic, script and stylesheet directories
        #app.mount("/css", StaticFiles(directory=directory_data_css), name="css")
        #app.mount("/data", StaticFiles(directory=directory_cache_json), name="data")
        #app.mount("/graphic", StaticFiles(directory=directory_data_graphic), name="graphic")
        #app.mount("/script", StaticFiles(directory=directory_data_script), name="script")
        #app.mount("/xsl", StaticFiles(directory=directory_data_xsl), name="xsl")
