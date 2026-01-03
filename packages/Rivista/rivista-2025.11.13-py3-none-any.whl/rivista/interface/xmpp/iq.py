#!/usr/bin/python
# -*- coding: utf-8 -*-

from rivista.utility.logger import UtilityLogger
from slixmpp.exceptions import IqError, IqTimeout
import sys

logger = UtilityLogger(__name__)

class InsterfaceXmppIQ:

    async def send(iq, timeout):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        try:
            await iq.send(timeout=timeout)
        except IqError as e:
            #raise Exception('IQ Error!')
            print(str(e))
        except IqTimeout as e:
            #raise Exception('IQ Timeout!')
            print(str(e))
        except Exception as e:
            #raise Exception('Error!')
            print(str(e))
