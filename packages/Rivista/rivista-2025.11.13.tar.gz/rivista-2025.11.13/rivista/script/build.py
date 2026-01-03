#!/usr/bin/python
# -*- coding: utf-8 -*-

#import importlib.resources

import asyncio
from concurrent.futures import ProcessPoolExecutor
import os
from rivista.interface.gemini.server import InterfaceGeminiServer
from rivista.interface.http.server import InterfaceHttpServer
#from rivista.interface.xmpp.client import xmpp_instance
from rivista.property.publish import publish_properties
from rivista.publish.gmi import PublishGmi
from rivista.publish.metalink import PublishMetalink
from rivista.publish.microsummary import PublishMicrosummary
from rivista.publish.opml import PublishOpml
from rivista.publish.osd import PublishOsd
from rivista.publish.sitemap import PublishSitemap
from rivista.publish.xml import PublishXml
from rivista.publish.xmpp import PublishXmpp
from rivista.utility.config import Cache, Data
from rivista.utility.logger import UtilityLogger
from rivista.utility.vcard import UtilityVCard
import shutil
#import socket
#import socks
import sys

def start():

    logger = UtilityLogger("rivista")

    #logger.set_level(loglevel)
    logger.set_level("debug")

    logger.debug("debug")
    logger.error("error")
    logger.info("info")
    logger.warning("warning")

    #s = socks.socksocket()
    #s.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)

    #socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050)
    #socket.socket

    directory_data = Data.get_directory()

    # Create data directories
    for directory in ("output", "sockets"):
        pathname = os.path.join(directory_data, directory)
        if not os.path.exists(pathname):
            os.mkdir(pathname)
            print(f"Creating directory {pathname}")

    # Create symlinks (i.e. shortcuts)
    directory_data_data = os.path.join(directory_data, "data")
    for directory in os.listdir(directory_data_data):
        directory_data_data_directory = os.path.join(directory_data_data, directory)
        directory_output = publish_properties.directory_output
        directory_output_directory = os.path.join(directory_output, directory)
        try:
            os.symlink(directory_data_data_directory, directory_output_directory)
        except FileExistsError:
            logger.info(f"Symlink already exists: {directory_output}")
        except PermissionError:
            logger.error(f"Permission denied for the creation of link: {directory_output}")
        except OSError as e:
            logger.error(f"OSError: {str(e)}")

    # Create symlinks (i.e. shortcuts)
    for directory in ("css", "xslt"):
        directory_output = publish_properties.directory_output
        directory_output_directory = os.path.join(directory_output, directory)
        directory_themes = publish_properties.directory_themes
        directory_themes_directory = os.path.join(
            directory_themes, publish_properties.theme, directory)
        try:
            os.symlink(directory_themes_directory, directory_output_directory)
        except FileExistsError:
            logger.info(f"Symlink already exists: {directory_output}")
        except PermissionError:
            logger.error(f"Permission denied for the creation of link: {directory_output}")
        except OSError as e:
            logger.error(f"OSError: {str(e)}")

    arguments = sys.argv[1:]
    if len(arguments) > 0:
        PublishXml.initiate()
        if "gemini" in arguments:
            if "xmpp" in arguments:
                PublishGmi.initiate()
            else:
                PublishGmi.initiate()
            #PublishGmi.contact()
        if "xmpp" in arguments:
            asyncio.run(PublishXmpp.initiate())
            asyncio.run(UtilityVCard.cache())
            #asyncio.run(PublishXml.comments_xmpp())
        #PublishXml.contact()
        PublishMetalink.initiate()
        PublishMicrosummary.initiate()
        if "osd" in arguments:
            PublishOsd.initiate()
        if "opml" in arguments:
            PublishOpml.initiate()
        if "sitemap" in arguments:
            PublishSitemap.initiate()
    else:
        PublishGmi.initiate()
        #PublishGmi.contact()
        PublishXml.initiate()
        PublishXml.contact()
        PublishMetalink.initiate()
        PublishMicrosummary.initiate()
        PublishOpml.initiate()
        PublishSitemap.initiate()

    """
    try:
        PublishGmi.initiate()
        PublishXml.initiate()
        asyncio.run(PublishXmpp.initiate())
        asyncio.run(UtilityVCard.cache())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(e)
    """
