#!/usr/bin/python
# -*- coding: utf-8 -*-

#import importlib.resources

import asyncio
from concurrent.futures import ProcessPoolExecutor
import os
from rivista.interface.gemini.server import InterfaceGeminiServer
from rivista.interface.http.server import InterfaceHttpServer
#from rivista.interface.xmpp.client import xmpp_instance
from rivista.publish.gmi import PublishGmi
from rivista.publish.xml import PublishXml
from rivista.publish.xmpp import PublishXmpp
from rivista.utility.config import Cache
from rivista.utility.logger import UtilityLogger
from rivista.utility.vcard import UtilityVCard
import shutil
import sys

def start():

    directory_cache = Cache.get_directory()

    filename_log = os.path.join(directory_cache,
                                "rivista_log.tsv")
    filename_log_old = os.path.join(directory_cache,
                                    "rivista_log.tsv.old")
    #filename_log = os.path.join(configurations.directory_cache,
    #                            "rivista_log.tsv")
    #filename_log_old = os.path.join(configurations.directory_cache,
    #                                "rivista_log.tsv.old")
    if os.path.exists(filename_log): os.rename(filename_log, filename_log_old)

    logger = UtilityLogger("rivista")

    #if not args.nolog:
    #logger.set_filename(filename_log)
    #with open(filename_log, "a") as file:
    #    file.write("Time	Level	Module	Function	Variable	Message\n")

    loglevel = "debug"
    logger.set_level(loglevel)

    logger.debug("debug")
    logger.error("error")
    logger.info("info")
    logger.warning("warning")

    arguments = sys.argv[1:]
    if len(arguments) > 0:
        if "gemini" in arguments and "http" in arguments:
            asyncio.run(start_instances())
        if "gemini" in arguments:
            InterfaceGeminiServer()
        elif "http" in arguments:
            InterfaceHttpServer()
    else:
        asyncio.run(start_instances())

async def start_instances():
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as executor:
        await asyncio.gather(
            loop.run_in_executor(executor, InterfaceHttpServer),
            loop.run_in_executor(executor, InterfaceGeminiServer)
        )

#async def start_instances():
#    await asyncio.gather(
#        asyncio.to_thread(InterfaceHttpServer),
#        asyncio.to_thread(InterfaceGeminiServer)
#    )
