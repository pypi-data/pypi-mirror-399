#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from rivista.parser.opml import ParserOpml
from rivista.parser.xml import ParserXml
from rivista.parser.xslt import ParserXslt
from rivista.property.publish import publish_properties
from rivista.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class PublishOpml:

    def initiate() -> None:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        PublishOpml.collection()

    def collection() -> None:
        """
        Create an OPML Collection.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        # NOTE /posts and /tags and for PubSub also /categories
        opml = {}
        opml["title"] = "OPML Collection"
        opml["description"] = "Rivista Voyager Subscriptions"
        opml["links"] = []
        opml["links"].append({
            "href" : "collection.opml",
            "rel"  : "self",
            "title" : "",
            "type"  : "application/opml+xml"})
        for link in publish_properties.settings_map["atom"]["link"]:
            opml["links"].append({
                "href"  : link["href"],
                #"hreflang" : link["hreflang"],
                "rel"   : link["rel"],
                "title" : link["title"] if "title" in link else "",
                "type"  : link["type"]})
        opml["items"] = []
        directory_output = publish_properties.directory_output
        for subdirectory in os.listdir(directory_output):
            pathname = os.path.join(directory_output, subdirectory)
            #if os.path.isdir(pathname) and len(os.listdir(pathname)) > 1:
            if os.path.isdir(pathname):
                list_of_dirs_and_files = os.listdir(pathname)
                if "index.atom" in list_of_dirs_and_files:
                    for dir_or_file in list_of_dirs_and_files:
                        pathname_ = os.path.join(pathname, dir_or_file)
                        if os.path.isdir(pathname_):
                            opml_item = {}
                            opml_item["text"] = subdirectory # TODO Extract title from index.atom
                            opml_item["xmlUrl"] = subdirectory
                            opml["items"].append(opml_item)
                            break
        filepath_opml = os.path.join(directory_output, "collection.opml")
        opml_as_string = ParserOpml.document(opml)
        with open(filepath_opml, "w") as fn: fn.write(opml_as_string)
        # Generate HTML of OPML
        #directory_xslt = publish_properties.directory_xslt
        #filepath_xslt = os.path.join(directory_xslt, "page-opml.xslt")
        #opml_as_element_tree = ParserXml.create_element_tree_from_file(filepath_opml)
        #opml_html_as_str = ParserXslt.transform_data(opml_as_element_tree, filepath_xslt)
        #filepath_opml_html = os.path.join(directory_output, "collection.html")
        #with open(filepath_opml_html, "w") as fn: fn.write(opml_html_as_str)
