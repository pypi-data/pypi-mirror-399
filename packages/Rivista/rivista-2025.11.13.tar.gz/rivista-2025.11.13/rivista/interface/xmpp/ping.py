#!/usr/bin/python
# -*- coding: utf-8 -*-

from rivista.utility.logger import UtilityLogger
#from slixmpp.exceptions import IqError, IqTimeout
import sys

logger = UtilityLogger(__name__)

class InterfaceXmppPing:

    async def to_self(xmpp_instance):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        rtt = await xmpp_instance.plugin['xep_0199'].ping()
        logger.info(f'{function_name},,Ping: {rtt}')
        logger.debug(f'{function_name},,Finish')
        return rtt
