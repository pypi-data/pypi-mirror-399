#!/usr/bin/python
# -*- coding: utf-8 -*-

from lxml import etree as lxml_etree
import xml.etree.ElementTree as xml_etree

class UtilityXml:

    def convert_lxml_to_xml(lxml_element: lxml_etree) -> xml_etree.Element:
        # Convert object lxml.etree._Element to string
        lxml_string = lxml_etree.tostring(lxml_element, encoding="unicode")
        # Parse the string as object xml.etree.ElementTree.Element
        return xml_etree.fromstring(lxml_string)
