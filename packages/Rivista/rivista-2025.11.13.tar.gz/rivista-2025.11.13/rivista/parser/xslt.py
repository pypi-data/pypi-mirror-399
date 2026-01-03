#!/usr/bin/python
# -*- coding: utf-8 -*-

import lxml.etree as ET
#from rivista.utility.logger import UtilityLogger
import sys
#import xml.etree.ElementTree as ET

#logger = UtilityLogger(__name__)

class ParserXslt:

    def transform_data(data: ET._Element, filepath_xslt: str) -> str:
        """Transform an XML document by a specified XSLT stylesheet filename."""
        xslt_stylesheet = ET.parse(filepath_xslt)
        xslt_transform = ET.XSLT(xslt_stylesheet)
        newdom = xslt_transform(data)
        #xml_data_bytes = ET.tostring(newdom, pretty_print=True)
        #xml_data_str = xml_data_bytes.decode("utf-8")
        xml_data_bytes = memoryview(newdom)
        xml_data_str = str(xml_data_bytes, "UTF-8")
        return xml_data_str
