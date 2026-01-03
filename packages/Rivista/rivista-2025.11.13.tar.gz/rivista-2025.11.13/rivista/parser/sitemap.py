#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from rivista.utility.logger import UtilityLogger
from rivista.version import __version__
import sys
#import xml.etree.ElementTree as ET
import lxml.etree as ET

logger = UtilityLogger(__name__)

class ParserSitemap:

    def sitemapindex(sitemap: dict):
        """
        Generate a Sitemap document.
        """
        e_sitemapindex = ET.Element("sitemapindex", nsmap={
            None    : "http://www.sitemaps.org/schemas/sitemap/0.9",
            "atom"  : "http://www.w3.org/2005/Atom",
            "xlink" : "http://www.w3.org/1999/xlink"})
        for link in sitemap["links"]:
            ET.SubElement(e_sitemapindex, "{http://www.w3.org/2005/Atom}link", {
                "href"  : link["href"],
                "rel"   : link["rel"],
                "title" : link["title"],
                "type"  : link["type"]})
        e_generator = ET.SubElement(
            e_sitemapindex, "{http://www.w3.org/2005/Atom}generator", {
                "uri"    : "https://git.xmpp-it.net/sch/Rivista",
                "version": f"{__version__}"})
        e_generator.text = "Rivista Voyager"
        for item in sitemap["items"]:
            e_sitemap = ET.SubElement(e_sitemapindex, "sitemap")
            ET.SubElement(e_sitemap, "loc").text = item["loc"]
            ET.SubElement(e_sitemap, "lastmod").text = item["lastmod"]
        xslt_reference = ET.ProcessingInstruction(
            "xml-stylesheet",
            "type=\"text/xml\" href=\"/xslt/page-sitemap.xslt\"")
        e_sitemapindex.addprevious(xslt_reference)
        xml_data = ET.ElementTree(e_sitemapindex)
        xml_data_bytes = ET.tostring(
            xml_data, pretty_print=True, xml_declaration=True, encoding="utf-8")
        xml_data_str = xml_data_bytes.decode("utf-8")
        return xml_data_str

    def urlset(sitemap: list):
        """
        Generate a Urlset document.
        """
        e_urlset = ET.Element("urlset", nsmap={
            None    : "http://www.sitemaps.org/schemas/sitemap/0.9",
            "atom"  : "http://www.w3.org/2005/Atom",
            "xlink" : "http://www.w3.org/1999/xlink"})
        for link in sitemap["links"]:
            ET.SubElement(e_urlset, "{http://www.w3.org/2005/Atom}link", {
                "href"  : link["href"],
                "rel"   : link["rel"],
                "title" : link["title"],
                "type"  : link["type"]})
        e_generator = ET.SubElement(
            e_urlset, "{http://www.w3.org/2005/Atom}generator")
        e_generator.text = "Rivista Voyager"
        for item in sitemap["items"]:
            e_url = ET.SubElement(e_urlset, "url")
            ET.SubElement(e_url, "loc").text = item["loc"]
            ET.SubElement(e_url, "lastmod").text = item["lastmod"]
            #e_url.set("changefreq", changefreq)
            #e_url.set("priority", priority)
        xslt_reference = ET.ProcessingInstruction(
            "xml-stylesheet",
            "type=\"text/xml\" href=\"/xslt/page-sitemap.xslt\"")
        e_urlset.addprevious(xslt_reference)
        xml_data = ET.ElementTree(e_urlset)
        xml_data_bytes = ET.tostring(
            xml_data, pretty_print=True, xml_declaration=True, encoding="utf-8")
        xml_data_str = xml_data_bytes.decode("utf-8")
        return xml_data_str
