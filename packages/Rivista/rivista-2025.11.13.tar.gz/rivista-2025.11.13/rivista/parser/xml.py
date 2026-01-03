#!/usr/bin/python
# -*- coding: utf-8 -*-

#from rivista.utility.logger import UtilityLogger
from rivista.version import __version__
import sys
#import xml.etree.ElementTree as ET
import lxml
import lxml.etree as ET
#from lxml import etree

#logger = UtilityLogger(__name__)

class ParserXml:

    def append_xml_to_xml(filepath_xslt, xhtml_content_str, expression_xpath):
        """
        Modify an XML file.
        
        This function, previously named "append_xhtml_to_xslt", was utilized to
        add custom elements to XSLT stylesheets.

        rst_content_str = open(filepath_rst, mode="r").read()
        expression_xpath = UtilityRst.value_of_metadata(
            rst_content_str, "xpath")
        xhtml_content_str = UtilityDocument.convert(
            rst_content_str, "xhtml")
        ParserXml.append_xhtml_to_xslt(filepath_xslt,
                                       xhtml_content_str,
                                       expression_xpath)

        Now, reStructuredText preambles that are converted into CSV, custom
        element atom:link, and XSLT directives that manage element atom:link
        handle that task.
        """
        # Load the existing XML file
        document_xslt = ET.parse(filepath_xslt)
        #root = document_xslt.getroot()
        element_xml = document_xslt.xpath(expression_xpath)
        if element_xml:
            subelement = ET.fromstring(xhtml_content_str)
            #subelement = etree.HTML(xhtml_content_str)
            #subelement = etree.XML(xhtml_content_str)
            element_xml[0].append(subelement)
        #return etree.tostring(document_xslt, pretty_print=True, encoding="unicode")
        #document_xslt = ET.ElementTree(root)
        document_xslt.write(filepath_xslt, pretty_print=True)

    def create_element_tree_from_file(filepath_xml: str) -> lxml.etree._Element:
        return ET.parse(filepath_xml)

    def create_element_tree_from_string(xml_content: str) -> lxml.etree._Element:
        return ET.fromstring(xml_content.encode("utf-8"))
