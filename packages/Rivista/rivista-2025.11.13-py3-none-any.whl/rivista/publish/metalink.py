#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
TODO
Iterate XML files for enclosures, detect thos enclosures and create Metalink
documents accordingly.

(Pdb) os.path.lexists.__doc__
'Test whether a path exists.  Returns True for broken symbolic links'
(Pdb) os.path.exists.__doc__
'Test whether a path exists.  Returns False for broken symbolic links'
"""

import os
from rivista.parser.atom import ParserAtom
from rivista.parser.metalink import ParserMetalink
from rivista.parser.toml import ParserToml
from rivista.parser.xml import ParserXml
from rivista.parser.xslt import ParserXslt
from rivista.property.publish import publish_properties
from rivista.utility.config import Data
from rivista.utility.csv import UtilityCsv
from rivista.utility.document import UtilityDocument
from rivista.utility.html import UtilityHtml
from rivista.utility.logger import UtilityLogger
from rivista.utility.rst import UtilityRst
from rivista.utility.text import UtilityText
from rivista.utility.uri import UtilityUri
import sys

logger = UtilityLogger(__name__)

class PublishMetalink:

    def initiate() -> None:
        """
        Scan the output directory for Atom Syndication Format documents;
        Detect instances of relation (attribute "rel") "enclosure"; and
        Upon detection thereof, generate Metalink files.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        directory_output = publish_properties.directory_output
        for root, directory, file in os.walk(directory_output):
            pathname_atom_file = os.pathname = os.path.join(root, "index.atom")
            if os.path.exists(pathname_atom_file):
                elements = ParserAtom.extract_element_link(
                    pathname_atom_file, "enclosure")
                metalink = {}
                metalink["dynamic"] = ""
                metalink["files"] = []
                metalink["origin"] = ""
                metalink["published"] = ""
                metalink["updated"] = ""
                metalink["links"] = []
                metalink["links"].append({
                    "href" : "enclosures.meta4",
                    "rel"  : "self",
                    "title" : "",
                    "type"  : "application/metalink+xml"})
                for link in publish_properties.settings_map["atom"]["link"]:
                    metalink["links"].append({
                        "href"  : link["href"],
                        #"hreflang" : link["hreflang"],
                        "rel"   : link["rel"],
                        "title" : link["title"] if "title" in link else "",
                        "type"  : link["type"]})
                for element in elements:
                    href = element.attrib["href"]
                    filename = filesize = ""
                    if "://" in href or not UtilityUri.has_scheme(href):
                        if href.startswith("ed2k"):
                            parameter_filename = parameter_filesize = False
                            for i in href.split("|"):
                                if parameter_filesize == True:
                                    filesize = i
                                    break
                                if parameter_filename == True:
                                    filename = i
                                    parameter_filesize = True
                                    continue
                                if i == "file":
                                    parameter_filename = True
                        else:
                            filename = os.path.basename(href)
                    else:
                        uri_parameters = UtilityUri.parameters(href)
                        if "dn" in uri_parameters:
                            filename = uri_parameters["dn"][0]
                        if "xl" in uri_parameters:
                            filesize = uri_parameters["xl"][0]
                    # If link is local (not URI), create a Metalink.
                    local = False
                    if filename:
                        if not UtilityUri.has_scheme(href):
                            local = True
                            if href.startswith("/"):
                                href = href[1:]
                            pathname_local = os.path.join(directory_output, href)
                            domain_name_gemini = publish_properties.domain_name_gemini
                            domain_name_http = publish_properties.domain_name_http
                            pathname_http = os.path.join(publish_properties.domain_name_http, href)
                            pathname_gemini = os.path.join(publish_properties.domain_name_gemini, href)
                        file = {}
                        file["name"] = filename
                        file["copyright"] = ""
                        file["description"] = element.attrib["title"]
                        file["identity"] = element.attrib["title"] # element.attrib["description"]
                        file["languages"] = []
                        file["logo"] = ""
                        if filesize:
                            file["size"] = filesize
                        elif os.path.exists(pathname_local):
                            file["size"] = str(os.path.getsize(pathname_local))
                        else:
                            file["size"] = ""
                        if local:
                            file["urls"] = [
                                {"location" : "1",
                                  "priority" : "1",
                                  "url" : pathname_gemini},
                                {"location" : "1",
                                  "priority" : "1",
                                  "url" : pathname_http}]
                        else:
                            file["urls"] = [
                                {"location" : "1",
                                  "priority" : "1",
                                  "url" : href}]
                        if ";" in element.attrib["type"]:
                            filetype, version = element.attrib["type"].split(";")
                        else:
                            filetype = version = ""
                        # NOTE Ask Metalinker to add element "metalink:mime".
                        file["mimetype"] = filetype
                        file["version"] = version.replace("version=", "").strip()
                        metalink["files"].append(file)
                data = ParserMetalink.meta4(metalink)
                pathname_metalink = os.path.join(root, "enclosures.meta4")
                try:
                    with open(pathname_metalink, "w") as fn: fn.write(data)
                except Exception as e:
                    logger.error(f"{function_name}		str(e)")
                    breakpoint()

