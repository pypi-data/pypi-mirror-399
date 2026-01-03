#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from rivista.parser.sitemap import ParserSitemap
from rivista.parser.toml import ParserToml
from rivista.parser.xslt import ParserXslt
from rivista.property.publish import publish_properties
from rivista.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class PublishSitemap:

    def initiate() -> None:
        """ Iterate directories and determine the creation of Sitemap or Urlset files. """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        directory_output = publish_properties.directory_output
        directories_first_level = []
        for first_level in os.listdir(directory_output):
            pathname_first_level = os.path.join(directory_output, first_level)
            if os.path.isdir(pathname_first_level): directories_first_level.append(first_level)
        PublishSitemap.sitemap("sitemap", directories_first_level)
        for directory_first_level in directories_first_level:
            pathname_directory_first_level = os.path.join(directory_output, directory_first_level)
            directories_second_level = []
            for second_level in os.listdir(pathname_directory_first_level):
                pathname_second_level = os.path.join(directory_output, directory_first_level, second_level)
                if os.path.isdir(pathname_second_level): directories_second_level.append(second_level)
            if directories_second_level:
                PublishSitemap.sitemap("urlset", directories_second_level, directory_first_level)

    def sitemap(kind, selection, directory="") -> None:
        """ Create a Sitemap or Urlset file. """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{kind}	Start")
        logger.debug(f"{function_name}	{directory}	Start")
        sitemap = {}
        sitemap["links"] = []
        filename_xml = f"{kind}.xml"
        sitemap["links"].append({
            "href" : f"/{directory}/{filename_xml}" if directory else f"/{filename_xml}",
            "rel"  : "self",
            "title" : "",
            "type"  : "application/xml"})
        for link in publish_properties.settings_map["atom"]["link"]:
            sitemap["links"].append({
                "href"  : link["href"],
                #"hreflang" : link["hreflang"],
                "rel"   : link["rel"],
                "title" : link["title"] if "title" in link else "",
                "type"  : link["type"]})
        sitemap["items"] = []
        for path in selection:
            sitemap_item = {}
            sitemap_item["loc"] = path
            sitemap_item["lastmod"] = path # TODO Extract value of updated from index.atom
            sitemap["items"].append(sitemap_item)
        filename_xml = f"{kind}.xml"
        # NOTE This is probably not a good practive.
        # TODO Consider to handle diretctories in a more sensible and uniform fashion.
        directory_output = publish_properties.directory_output
        filepath_xml = os.path.join(directory_output, directory, filename_xml)
        filename_xslt = "page-sitemap.xslt"
        match kind:
            case "sitemap":
                sitemap_as_string = ParserSitemap.sitemapindex(sitemap)
            case "urlset":
                sitemap_as_string = ParserSitemap.urlset(sitemap)
        with open(filepath_xml, "w") as fn: fn.write(sitemap_as_string)
        # Generate HTML of Sitemap
        #directory_xslt = publish_properties.directory_xslt
        #filepath_xslt = os.path.join(directory_xslt, filename_xslt)
        #sitemap_html_as_str = ParserXslt.transform_data(filepath_xml, filepath_xslt)
        #filepath_xml_html = os.path.join(directory_output, f"{kind}.html")
        #with open(filepath_xml_html, "w") as fn: fn.write(sitemap_html_as_str)
