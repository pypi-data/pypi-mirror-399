#!/usr/bin/python
# -*- coding: utf-8 -*-

# TODO Update to version 2.0 http://opml.org/spec2.opml

import datetime
from rivista.utility.logger import UtilityLogger
from rivista.version import __version__
import sys
#import xml.etree.ElementTree as ET
import lxml.etree as ET

logger = UtilityLogger(__name__)

class ParserOpml:

    def document(opml: dict):
        """
        Generate an OPML Collection document.
        """
        e_opml = ET.Element("opml", nsmap={
            "atom"  : "http://www.w3.org/2005/Atom",
            "xlink" : "http://www.w3.org/1999/xlink"})
        e_opml.set("version", "1.0")
        if "links" in opml:
            for link in opml["links"]:
                ET.SubElement(e_opml, "{http://www.w3.org/2005/Atom}link", {
                    "href"  : link["href"],
                    "rel"   : link["rel"],
                    "title" : link["title"],
                    "type"  : link["type"]})
        e_head = ET.SubElement(e_opml, "head")
        e_title = ET.SubElement(e_head, "title")
        e_title.text = "OPML Collection"
        e_description = ET.SubElement(e_head, "description")
        e_description.text = "Rivista Voyager Subscriptions"
        e_generator = ET.SubElement(
            e_head, "{http://www.w3.org/2005/Atom}generator", {
                "uri"    : "https://git.xmpp-it.net/sch/Rivista",
                "version": f"{__version__}"})
        e_generator.text = "Rivista Voyager"
        e_urlpublic = ET.SubElement(e_head, "urlPublic")
        e_urlpublic.text = "https://git.xmpp-it.net/sch/Rivista"
        time_stamp = datetime.datetime.now(datetime.UTC).isoformat()
        ET.SubElement(e_head, "dateCreated").text = time_stamp
        ET.SubElement(e_head, "dateModified").text = time_stamp
        e_body = ET.SubElement(e_opml, "body")
        for item in opml["items"]:
            e_outline = ET.SubElement(e_body, "outline")
            e_outline.set("text", item["text"])
            e_outline.set("xmlUrl", item["xmlUrl"])
        xslt_reference = ET.ProcessingInstruction(
            "xml-stylesheet",
            "type=\"text/xml\" href=\"/xslt/page-opml.xslt\"")
        e_opml.addprevious(xslt_reference)
        xml_data = ET.ElementTree(e_opml)
        xml_data_bytes = ET.tostring(
            xml_data, pretty_print=True, xml_declaration=True, encoding="utf-8")
        xml_data_str = xml_data_bytes.decode("utf-8")
        return xml_data_str
