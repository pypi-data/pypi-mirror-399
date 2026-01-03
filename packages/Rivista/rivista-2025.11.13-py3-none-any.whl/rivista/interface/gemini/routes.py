#!/usr/bin/python
# -*- coding: utf-8 -*-

from jetforce import JetforceApplication, RateLimiter, Request, Response, Status
import os
from rivista.interface.gemini.rates import (
    general_rate_limiter,
    long_rate_limiter,
    short_rate_limiter)
from rivista.property.publish import publish_properties
from rivista.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

routes = JetforceApplication(rate_limiter=general_rate_limiter)

class InterfaceGeminiRoutes:

    @routes.route("", strict_trailing_slash=False)
    @short_rate_limiter.apply
    def root(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        filename = publish_properties.filename_atom_gmi
        data = open(filename, mode="r")
        result = data.read()
        response = Response(
            Status.SUCCESS,
            "text/gemini",
            result)
        return response

    @routes.route("/graphics/(?P<filename>[.\dA-Za-z]+)")
    def graphics(request: Request, filename: str):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        pathname = os.path.join(publish_properties.directory_graphics,
                                f"{filename}")
        data = open(pathname, mode="br")
        result = data.read()
        response = Response(
            Status.SUCCESS,
            #"image/svg+xml",
            "application/octet-stream",
            result)
        return response

    @routes.route("/(?P<directory>[-\dA-Za-z0-9]+)")
    #@routes.route("/(?P<directory>[-\dA-Za-z0-9]+)/", strict_trailing_slash=True)
    @routes.route("/(?P<directory>[-\dA-Za-z0-9]+)/(?P<identifier>[-\dA-Za-z0-9]+)")
    @routes.route("/(?P<directory>[-\dA-Za-z0-9]+)/(?P<identifier>[-\dA-Za-z0-9]+)/(?P<filename>[-\dA-Za-z0-9]+)")
    def pages(request: Request, directory="", identifier="", filename="index.gmi"):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        if not request.path.endswith("/"):
            response = Response(
                Status.REDIRECT_PERMANENT,
                f"{request.url}/")
        elif not identifier and not request.path.endswith("/"):
            response = Response(
                Status.REDIRECT_PERMANENT,
                f"/{directory}/")
        else:
            filepath = os.path.join(publish_properties.directory_output,
                                    directory, identifier, filename)
            pathname = os.path.join(publish_properties.directory_output,
                                    directory, identifier, "index.gmi")
            if filename and os.path.exists(filepath):
                data = open(filepath, mode="r")
                result = data.read()
                response = Response(
                    Status.SUCCESS,
                    "text/gemini",
                    result)
            elif os.path.exists(pathname):
                data = open(pathname, mode="r")
                result = data.read()
                response = Response(
                    Status.SUCCESS,
                    "text/gemini",
                    result)
                #response = Response(
                #    Status.REDIRECT_PERMANENT,
                #    f"/{identifier}/")
            else:
                response = Response(
                    Status.NOT_FOUND,
                    f"Document {identifier} does not exist.")
        return response
