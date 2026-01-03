#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from rivista.parser.osd import ParserOsd
from rivista.property.publish import publish_properties
from rivista.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class PublishOsd:

    def initiate() -> None:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        PublishOsd.osd()

    def osd() -> None:
        directory_output = publish_properties.directory_output
        filepath_osd = os.path.join(directory_output, "search.osd")
        osd_as_string = ParserOsd.generate()
        with open(filepath_osd, "w") as fn: fn.write(osd_as_string)
