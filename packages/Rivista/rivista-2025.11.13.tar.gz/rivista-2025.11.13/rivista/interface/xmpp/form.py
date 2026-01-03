#!/usr/bin/python
# -*- coding: utf-8 -*-

from rivista.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class DataForm:

    def create_setting_entry(xmpp_instance, key : str, value : str):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        form = xmpp_instance['xep_0004'].make_form('form', 'Settings')
        form['type'] = 'result'
        form.add_field(var=key, value=value)
        return form

#    def create_setting_entry(value : str):
#        function_name = sys._getframe().f_code.co_name
#        logger.debug(f'{function_name},,Start')
#        element = ET.Element('value')
#        element.text = value
#        return element
