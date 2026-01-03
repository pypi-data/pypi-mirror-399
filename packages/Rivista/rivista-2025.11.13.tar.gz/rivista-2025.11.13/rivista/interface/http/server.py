#!/usr/bin/python
# -*- coding: utf-8 -*-

from aiohttp import web as HttpServer
import asyncio
from rivista.interface.http.application import HttpApplication
from rivista.interface.http.errors import HttpErrors
from rivista.interface.http.middleware import HttpMiddleware
from rivista.interface.http.routes import HttpRoutes, routes
from rivista.property.publish import publish_properties
from rivista.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class InterfaceHttpServer:

    def __init__(self):
        #app = HttpServer.Application()
        app = HttpServer.Application(
            middlewares=[
                HttpMiddleware.user_agent_check,
                HttpMiddleware.operating_system_check
            ]
        )
        app.on_startup.append(HttpApplication.initiate)
        app.add_routes(routes)
        #app.router.add_get("/index.atom", HttpRoutes.atom, name="atom")
        app.router.add_get("/", HttpRoutes.main_html, name="root")
        HttpErrors.setup_middlewares(app)
        #asyncio.create_task(HttpServer.run_app(app, port=8080))
        settings = publish_properties.settings["server"]["http"]
        #hostname = settings["hostname"]
        host = settings["host"]
        port = settings["port"]
        HttpServer.run_app(app, host=host, port=port)

        #asyncio.run(HttpApplication.initiate())
        #asyncio.create_task(HttpIpc.server())

        # Mount static graphic, script and stylesheet directories
        #app.mount("/css", StaticFiles(directory=directory_data_css), name="css")
        #app.mount("/data", StaticFiles(directory=directory_cache_json), name="data")
        #app.mount("/graphic", StaticFiles(directory=directory_data_graphic), name="graphic")
        #app.mount("/script", StaticFiles(directory=directory_data_script), name="script")
        #app.mount("/xsl", StaticFiles(directory=directory_data_xsl), name="xsl")
