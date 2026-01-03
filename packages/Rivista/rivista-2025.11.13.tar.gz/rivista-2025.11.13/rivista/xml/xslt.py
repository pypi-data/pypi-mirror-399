#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

class XmlXslt:

    """This is a patch function to append XSLT reference to XML."""
    """Why is there no built-in function of ElementTree or LXML?"""
    def append_stylesheet(xml_data, type):
        # Register namespace in order to avoide ns0:
        if type == 'atom': ET.register_namespace('', 'http://www.w3.org/2005/Atom')
        # Load XML from string
        tree = ET.fromstring(xml_data)
        # The following direction removes the XML declaration
        xml_data_without_a_declaration = ET.tostring(tree, encoding='unicode')
        # Add XML declaration and stylesheet
        xml_data_declaration = (
            '<?xml version="1.0" encoding="utf-8"?>'
            '<?xml-stylesheet type="text/xsl" href="xsl/{}.xsl"?>'.format(type) +
            xml_data_without_a_declaration)
        return xml_data_declaration
