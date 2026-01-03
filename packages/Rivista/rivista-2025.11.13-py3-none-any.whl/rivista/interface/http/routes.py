#!/usr/bin/python
# -*- coding: utf-8 -*-

from aiohttp.web import (
    FileResponse,
    HTTPFound,
    Request,
    Response,
    RouteTableDef)
import asyncio
#import glob
import mimetypes
import os
from rivista.compiler.atom import CompilerAtom
from rivista.interface.http.errors import HttpErrors
from rivista.interface.xmpp.client import InterfaceXmppClient
from rivista.interface.xmpp.message import InterfaceXmppMessage
from rivista.interface.xmpp.ping import InterfaceXmppPing
from rivista.property.publish import publish_properties
from rivista.parser.xml import ParserXml
from rivista.parser.xslt import ParserXslt
from rivista.publish.xml import PublishXml
from rivista.utility.logger import UtilityLogger
from rivista.utility.search import UtilitySearch
import sys

logger = UtilityLogger(__name__)

routes = RouteTableDef()

class HttpRoutes:

    def file_handler(request: Request, filename, directory=""):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        """
        match directory:
            case "css":
                open_mode = "r"
                mimetype = "text/css"
            case "enclosures":
                open_mode = "rb"
                # NOTE Should filetype be checked for?
                mimetype = "application/octet-stream"
            case "graphics":
                open_mode = "rb"
                # NOTE Should filetype be checked for?
                mimetype = "image/svg+xml"
            case "images":
                open_mode = "rb"
                # NOTE Should filetype be checked for?
                mimetype = "application/octet-stream"
            case "profile":
                open_mode = "rb"
                # NOTE Should filetype be checked for?
                mimetype = "application/octet-stream"
            case "scripts":
                open_mode = "r"
                # NOTE application/ecmascript
                mimetype = "text/javascript"
            case "xslt":
                open_mode = "r"
                # NOTE
                # MIME-Type (content type) should be "text/xsl" or
                # "application/xslt+xml".
                # The reason for utilizing the text "application/xml" is so that
                # it be rendered in browsers of vendors that try to suppress the
                # XSLT technology.
                mimetype = "application/xml"
            case _:
                open_mode = "rb"
                mimetype = "application/octet-stream"
        """
        pathname = os.path.join(publish_properties.directory_output,
                                directory, filename)
        if os.path.exists(pathname):
            # TODO Consider to store a dictionary of filenames and mimetypes
            #      thereof, to save processing power circles.
            filetype, encoding = mimetypes.guess_type(pathname)
            # NOTE OSD is not included in the index of module mimetypes.
            if filetype:
                if "text" in filetype:
                    open_mode = "r"
                    mimetype = filetype
                elif "image" in filetype:
                    open_mode = "rb"
                    mimetype = filetype
                elif filetype == "application/xhtml+xml":
                    open_mode = "r"
                    mimetype = "text/html"
                elif "xml" in filetype:
                    open_mode = "r"
                    mimetype = "application/xml"
                else:
                    open_mode = "rb"
                    mimetype = "application/octet-stream"
            else:
                open_mode = "rb"
                mimetype = "application/octet-stream"
            result = open(pathname, mode=open_mode).read()
            if open_mode == "r":
                response = Response(
                    text=result,
                    content_type=mimetype)
            else:
                response = Response(
                    body=result,
                    content_type=mimetype)
        else:
            response = HttpErrors.handle_404(request)
        return response

    def check(request: Request):
        """
        Check whether an image (e.g. "so called invisible pixel") is ~loaded~
        requested.

        If no request was detected after a few seconds, then suppose that a
        given HTTP client does not support XSLT.

        If not, then redirect to an HTML version."
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")

    @routes.get("/")
    def main_routine(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        filename = publish_properties.filename_atom
        mimetype = "application/xml"
        result = open(filename, mode="r").read()
        response = Response(
            text=result,
            content_type=mimetype)
        return response

    @routes.get("/index.atom")
    def main_xml(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        filename = publish_properties.filename_atom
        mimetype = "application/xml"
        result = open(filename, mode="r").read()
        response = Response(
            text=result,
            content_type=mimetype)
        return response

    @routes.get("/index.html")
    def main_html(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        filename = publish_properties.filename_atom_html
        mimetype = "text/html"
        result = open(filename, mode="r").read()
        response = Response(
            text=result,
            content_type=mimetype)
        return response

    @routes.get("/xml")
    @routes.get("/xml/")
    @routes.get("/rss")
    @routes.get("/rss/")
    @routes.get("/feed")
    @routes.get("/feed/")
    @routes.get("/atom")
    @routes.get("/atom/")
    def main_xml_redirect(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        #location = request.app.router["atom"].url_for()
        #raise HTTPFound(location=location)
        raise HTTPFound("/index.atom")

    @routes.get("/urlset.xml")
    @routes.get("/sitemap.xml")
    @routes.get("/{directory}/urlset.xml")
    def sitemap(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        directory_output = publish_properties.directory_output
        if "directory" in request.match_info:
            directory = request.match_info["directory"]
            pathname = os.path.join(directory_output, directory, "urlset.xml")
        else:
            filename = request.path.split("/")[1]
            pathname = os.path.join(directory_output, filename)
        result = open(pathname, mode="r").read()
        response = Response(
            text=result,
            content_type="application/xml")
        return response

    @routes.get("/{identifier}/comments.atom")
    @routes.get("/{directory}/{identifier}/comments.atom")
    def comments_xml(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        return HttpRoutes.comments(request, xml=True)

    @routes.get("/{identifier}/comments.html")
    @routes.get("/{directory}/{identifier}/comments.html")
    def comments_html(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        return HttpRoutes.comments(request, xml=False)

    def comments(request: Request, xml=True):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        if "directory" in request.match_info:
            directory = request.match_info["directory"]
        else:
            directory = ""
        if directory not in ("graphics", "images", "scripts"):
            if "identifier" in request.match_info:
                identifier = request.match_info["identifier"]
            else:
                identifier = "index"
            #PublishXml.edit(rst_page_pathname, identifier, directory)
            result = None
            if xml:
                pathname = os.path.join(publish_properties.directory_output,
                                        directory, identifier, "comments.atom")
                if os.path.exists(pathname):
                    result = open(pathname, mode="r").read()
                    content_type="application/xml"
            else:
                pathname = os.path.join(publish_properties.directory_output,
                                        directory, identifier, "comments.html")
                if os.path.exists(pathname):
                    result = open(pathname, mode="r").read()
                    content_type="text/html"
            if not result:
                result = "No comments section is available for this document."
                content_type="text/plain"
        response = Response(
            text=result,
            content_type=content_type)
        return response

    @routes.get("/{identifier}/comments")
    @routes.get("/{directory}/{identifier}/comments")
    def comments_redirect(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        raise HTTPFound(f"{request.raw_path}.html")

    @routes.post("/comment")
    async def comment(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        data = await request.post()
        address = data["address"]
        title = data["title"]
        comment = data["comment"]
        details = (
            f"Address\n-------\n\n{address}\n\n\n"
            f"Title\n-------\n\n{title}\n\n\n"
            f"Comment\n-------\n\n{comment}")
        address = publish_properties.address
        password = publish_properties.password
        xmpp_instance = InterfaceXmppClient(address, password)
        rtt = await InterfaceXmppPing.to_self(xmpp_instance)
        if xmpp_instance.is_connected or rtt:
            message_body = (
                "A comment was sent from Rivista contact form.\n\n"
                f"IP Address\n----------\n\n{request.remote}\n\n\n"
                f"{details}\n\n"
                f"To approve this comment, send command: Approve {identifier}")
            jid_bare = xmpp_instance.boundjid.bare
            InterfaceXmppMessage.send(xmpp_instance, jid_bare, message_body)
        result = (
            "SENT INFORMATION\n================\n\n"
            f"Your comment was sent. See details further.\n\n\n{details}")
        response = Response(
            text=result,
            content_type="text/plain")
        return response

    async def search(request: Request, query=None, parameters=None, xml=True):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        if query:
            atom = await UtilitySearch.query(query, parameters)
            #filename_xslt = "atom.xslt"
            filename_xslt = "/xslt/page-search.xslt"
            atom_as_string = CompilerAtom.syndication_format(atom, filename_xslt)
            if xml:
                result = atom_as_string
                content_type="application/xml"
            else:
                directory_xslt = publish_properties.directory_xslt
                filepath_xslt = os.path.join(directory_xslt, filename_xslt)
                atom_as_element_tree = ParserXml.create_element_tree_from_string(
                    atom_as_string)
                atom_html_as_str = ParserXslt.transform_data(
                    atom_as_element_tree, filepath_xslt)
                result = atom_html_as_str
                content_type="text/html"
        elif xml:
            pathname = os.path.join(
                publish_properties.directory_output, "search", "index.atom")
            if os.path.exists(pathname):
                result = open(pathname, mode="r").read()
                content_type="application/xml"
        else:
            pathname = os.path.join(
                publish_properties.directory_output, "search", "index.html")
            if os.path.exists(pathname):
                result = open(pathname, mode="r").read()
                content_type="text/html"
        response = Response(
            text=result,
            content_type=content_type)
        return response

    @routes.get("/search/")
    async def search_routine_get(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        request_query = request.rel_url.query
        if "query" in request_query:
            query = request_query["query"]
        else:
            query = None
        parameters = []
        for parameter in ["content", "summary", "title"]:
            if parameter in request_query and request_query[parameter] == "yes":
                parameters.append(parameter)
        return await HttpRoutes.search(request, query=query, parameters=parameters)

    @routes.get("/search/index.atom")
    async def search_xml_get(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        request_query = request.rel_url.query
        if "query" in request_query:
            query = request_query["query"]
        else:
            query = None
        parameters = []
        for parameter in ["content", "summary", "title"]:
            if parameter in request_query and request_query[parameter] == "yes":
                parameters.append(parameter)
        return await HttpRoutes.search(request, query=query, parameters=parameters, xml=True)

    @routes.get("/search/index.html")
    async def search_html_get(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        request_query = request.rel_url.query
        if "query" in request_query:
            query = request_query["query"]
        else:
            query = None
        parameters = []
        for parameter in ["content", "summary", "title"]:
            if parameter in request_query and request_query[parameter] == "yes":
                parameters.append(parameter)
        return await HttpRoutes.search(request, query=query, parameters=parameters, xml=False)

    @routes.post("/search/")
    async def search_html_post(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        request_post = await request.post()
        if "query" in request_post:
            query = request_post["query"]
        else:
            query = None
        parameters = []
        for parameter in ["content", "summary", "title"]:
            if parameter in request_post and request_post[parameter] == "yes":
                parameters.append(parameter)
        return await HttpRoutes.search(request, query=query, parameters=parameters)

    @routes.post("/search/index.atom")
    async def search_xml_post(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        request_post = await request.post()
        if "query" in request_post:
            query = request_post["query"]
        else:
            query = None
        parameters = []
        for parameter in ["content", "summary", "title"]:
            if parameter in request_post and request_post[parameter] == "yes":
                parameters.append(parameter)
        return await HttpRoutes.search(request, query=query, parameters=parameters, xml=True)

    @routes.get("/{identifier}/edit.atom")
    @routes.get("/{directory}/{identifier}/edit.atom")
    def edit_xml(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        return HttpRoutes.edit(request, xml=True)

    @routes.get("/{identifier}/edit.html")
    @routes.get("/{directory}/{identifier}/edit.html")
    def edit_html(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        return HttpRoutes.edit(request)

    def edit(request: Request, xml=False):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        if "directory" in request.match_info:
            directory = request.match_info["directory"]
        else:
            directory = ""
        if directory not in ("graphics", "images", "scripts"):
            if "identifier" in request.match_info:
                identifier = request.match_info["identifier"]
            else:
                identifier = "index"
            result = None
            rst_page_pathname = os.path.join(
                publish_properties.directory_source,
                directory, f"{identifier}.rst")
            if os.path.exists(rst_page_pathname):
                PublishXml.edit(rst_page_pathname, identifier, directory)
                if xml:
                    pathname = os.path.join(publish_properties.directory_output,
                                            directory, identifier, "edit.atom")
                    if os.path.exists(pathname):
                        result = open(pathname, mode="r").read()
                        content_type="application/xml"
                else:
                    pathname = os.path.join(publish_properties.directory_output,
                                            directory, identifier, "edit.html")
                    if os.path.exists(pathname):
                        result = open(pathname, mode="r").read()
                        content_type="text/html"
            if not result:
                result = "No source is available for this document."
                content_type="text/plain"
            response = Response(
                text=result,
                content_type=content_type)
            return response

    @routes.get("/{directory}/")
    @routes.get("/{directory}/{identifier}/")
    def pages_routine(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        logger.debug(f"{function_name}	request.raw_path	{request.raw_path}")
        return HttpRoutes.pages(request, xml=True)

    @routes.get("/{directory}/index.atom")
    @routes.get("/{directory}/{identifier}/index.atom")
    def pages_xml(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        return HttpRoutes.pages(request, xml=True)

    @routes.get("/{directory}/index.html")
    @routes.get("/{directory}/{identifier}/index.html")
    def pages_html(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        return HttpRoutes.pages(request, xml=False)

    def pages(request: Request, xml=True):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        if "directory" in request.match_info:
            directory = request.match_info["directory"]
        else:
            directory = ""
        if directory not in ("graphics", "images", "scripts"):
            if "identifier" in request.match_info:
                identifier = request.match_info["identifier"]
            else:
                identifier = ""
            if xml:
                filename = "index.atom"
                mimetype = "application/xml" # application/atom+xml
            else:
                filename = "index.html"
                mimetype = "text/html"
            pathname = os.path.join(publish_properties.directory_output,
                                    directory, identifier, filename)

#            if filename:
#                pathname = os.path.join(publish_properties.directory_output,
#                                        directory, identifier, filename)
#            else:
#                pathname = glob.glob(
#                    os.path.join(
#                        publish_properties.directory_output,
#                        directory, identifier, "index.*"))

            if os.path.exists(pathname):
                result = open(pathname, mode="r").read()
                response = Response(
                    text=result,
                    content_type=mimetype)
            elif not os.path.exists(pathname):
                #logger.error(f"{function_name}		{e}")
                # NOTE This condition is redundant.
                if directory not in ("graphics", "images", "scripts"):
                    raise HTTPFound(f"{request.raw_path}/")
                else:
                    # NOTE Error 403 might be better appropriate.
                    response = HttpErrors.handle_404(request)
            return response

    @routes.get("/{level_one}")
    @routes.get("/{level_one}/{level_two}")
    @routes.get("/{level_one}/{level_two}/{level_three}")
    def file_or_pages_redirect(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        level_one = level_two = level_three = ""
        if "level_one" in request.match_info:
            level_one = request.match_info["level_one"]
        if "level_two" in request.match_info:
            level_two = request.match_info["level_two"]
        if "level_three" in request.match_info:
            level_three = request.match_info["level_three"]
        if level_one and level_two and level_three:
            filename = level_three
            directory = os.path.join(level_one, level_two)
        elif level_one and level_two:
            filename = level_two
            directory = level_one
        else:
            filename = level_one
            directory = ""
        directory_output = publish_properties.directory_output
        pathname = os.path.join(directory_output, directory, filename)
        if os.path.exists(pathname):
            return HttpRoutes.file_handler(request, filename, directory)
        else:
            raise HTTPFound(f"{request.raw_path}/")

    @routes.get("/collection.opml")
    def collection_xml(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        return HttpRoutes.collection(request, xml=True)

    @routes.get("/collection.html")
    def collection_html(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        return HttpRoutes.collection(request, xml=False)

    def collection(request: Request, xml=True):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        if xml:
            filename = publish_properties.filename_opml
            result = open(filename, mode="r").read()
            content_type="application/xml"
        else:
            filename = publish_properties.filename_opml_html
            result = open(filename, mode="r").read()
            content_type="text/html"
        response = Response(
            text=result,
            content_type=content_type)
        return response

    @routes.get("/opml")
    @routes.get("/opml/")
    def collection_redirect(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        raise HTTPFound("/collection.opml")

    @routes.get("/links")
    @routes.get("/links/")
    @routes.get("/collection")
    @routes.get("/collection/")
    @routes.get("/subscriptions")
    @routes.get("/subscriptions/")
    def collection_redirect(request: Request):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        raise HTTPFound("/collection.html")

    @routes.post("/message")
    async def message(request: Request):
        data = await request.post()
        address = data["address"]
        subject = data["subject"]
        message = data["message"]
        details = (
            f"Address\n-------\n\n{address}\n\n\n"
            f"Subject\n-------\n\n{subject}\n\n\n"
            f"Message\n-------\n\n{message}")
        address = publish_properties.address
        password = publish_properties.password
        xmpp_instance = InterfaceXmppClient(address, password)
        rtt = await InterfaceXmppPing.to_self(xmpp_instance)
        if xmpp_instance.is_connected or rtt:
            message_body = (
                "A message was sent from Rivista contact form.\n\n"
                f"IP Address\n----------\n\n{request.remote}\n\n\n"
                f"{details}")
            jid_bare = xmpp_instance.boundjid.bare
            InterfaceXmppMessage.send(xmpp_instance, jid_bare, message_body)
        result = (
            "SENT INFORMATION\n================\n\n"
            f"Your message was sent. See details further.\n\n\n{details}")
        response = Response(
            text=result,
            content_type="text/plain")
        return response
