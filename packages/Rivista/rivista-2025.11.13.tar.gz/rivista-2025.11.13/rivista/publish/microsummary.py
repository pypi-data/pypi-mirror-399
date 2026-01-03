#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from rivista.parser.toml import ParserToml
from rivista.parser.atom import ParserAtom
from rivista.property.publish import publish_properties
from rivista.utility.config import Data
from rivista.utility.logger import UtilityLogger
from rivista.utility.uri import UtilityUri
import sys

logger = UtilityLogger(__name__)

class PublishMicrosummary:

    def initiate() -> None:
        """
        Scan the output directory for Atom Syndication Format documents;
        Detect instances of relation (attribute "rel") "microsummary"; and
        Upon detection thereof, generate plain text files from attribute "title".
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        directory_output = publish_properties.directory_output
        for root, directory, file in os.walk(directory_output):
            pathname_atom_file = os.pathname = os.path.join(root, "index.atom")
            if os.path.exists(pathname_atom_file):
                elements = ParserAtom.extract_element_link(
                    pathname_atom_file, "microsummary")
                for element in elements:
                    href = element.attrib["href"]
                    text = element.attrib["title"]
                    # If link is local (not URI), create a Microsummary.
                    if not UtilityUri.has_scheme(href):
                        if href.startswith("/"):
                            pathname = os.path.join(directory_output, href[1:])
                        else:
                            pathname = os.path.join(root, href)
                        try:
                            with open(pathname, "w") as fn: fn.write(text)
                        except Exception as e:
                            logger.error(f"{function_name}		str(e)")
