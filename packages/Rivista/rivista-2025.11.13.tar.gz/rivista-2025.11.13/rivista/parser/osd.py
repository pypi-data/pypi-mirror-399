#!/usr/bin/python
# -*- coding: utf-8 -*-

from rivista.property.publish import publish_properties
from rivista.utility.logger import UtilityLogger
import sys
#import xml.etree.ElementTree as ET
import lxml.etree as ET

logger = UtilityLogger(__name__)

class ParserOsd:

    def generate():
        """
        Generate an OpenSearchDescription document.
        """
        e_osd = ET.Element("OpenSearchDescription")
        e_osd.set("xmlns", "http://a9.com/-/spec/opensearch/1.1/")
        settings_search = publish_properties.settings["search"]
        e_language = ET.SubElement(e_osd, "Language")
        e_language.text = settings_search["language"]
        e_short_name = ET.SubElement(e_osd, "ShortName")
        e_short_name.text = settings_search["name"]["short"]
        e_long_name = ET.SubElement(e_osd, "LongName")
        e_long_name.text = settings_search["name"]["long"]
        e_description = ET.SubElement(e_osd, "Description")
        e_description.text = settings_search["description"]

        domain_name = publish_properties.settings["domain-name"]["http"]

        #e_image = ET.SubElement(e_osd, "Image")
        #e_image.text = f"{domain_name}/logo.png"
        #e_image.set("height", "32")
        #e_image.set("width", "32")
        #e_image.set("type", "image/png")

        #e_image_ico = ET.SubElement(e_osd, "Image")

        e_url_search = ET.SubElement(e_osd, "Url")
        e_url_search.set("method", "get")
        e_url_search.set(
            "template",
            domain_name + "/search/?query={searchTerms}&page={startPage}")
        #e_url_search.set("method", "post")
        #e_url_search.set("template", f"{domain_name}/search/")
        #e_url_suggestion = ET.SubElement(e_osd, "Url")
        #e_url_suggestion.set("method", "post")
        #e_url_suggestion.set("template", f"{domain_name}/suggestions")
        #e_url_suggestion.set("type", "application/x-suggestions+json")
        #e_param_query = ET.SubElement(e_osd, "Param")
        #e_param_query.set("name", "query")
        #e_param_query.set("value", "{searchTerms}")
        #e_param_page = ET.SubElement(e_osd, "Param")
        #e_param_page.set("name", "page")
        #e_param_page.set("value", "{startPage}")
        e_url_search.set("type", "text/html")
        e_input_encoding = ET.SubElement(e_osd, "InputEncoding")
        e_input_encoding.text = settings_search["encoding"]["input"]
        e_output_encoding = ET.SubElement(e_osd, "OutputEncoding")
        e_output_encoding.text = settings_search["encoding"]["output"]
        e_attribution = ET.SubElement(e_osd, "Attribution")
        e_attribution.text = settings_search["attribution"]
        e_contact = ET.SubElement(e_osd, "Contact")
        e_contact.text = settings_search["contact"]
        e_syndication_right = ET.SubElement(e_osd, "SyndicationRight")
        e_syndication_right.text = settings_search["syndication_right"]
        xslt_reference = ET.ProcessingInstruction(
            "xml-stylesheet",
            "type=\"text/xml\" href=\"/xslt/osd.xslt\"")
        e_osd.addprevious(xslt_reference)
        xml_data = ET.ElementTree(e_osd)
        xml_data_bytes = ET.tostring(
            xml_data, pretty_print=True, xml_declaration=True, encoding="utf-8")
        xml_data_str = xml_data_bytes.decode("utf-8")
        return xml_data_str
