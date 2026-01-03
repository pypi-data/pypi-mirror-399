#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from rivista.utility.logger import UtilityLogger
from slixmpp import Iq
from slixmpp.exceptions import IqError, IqTimeout
import sys

logger = UtilityLogger(__name__)

class InterfaceXmppVCard:

    async def retrieve(xmpp_instance) -> Iq:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        jid_bare = xmpp_instance.boundjid.bare
        iq = xep = None
        try:
            iq = await xmpp_instance.plugin["xep_0292"].retrieve_vcard(jid_bare)
            xep = "0292"
        except (Exception, IqError, IqTimeout) as e:
            logger.error(f"{function_name}		{str(e)}")
        if not isinstance(iq, Iq):
            try:
                iq = await xmpp_instance.plugin["xep_0054"].get_vcard(jid=jid_bare)
                xep = "0054"
            except:
                logger.error(f"{function_name}		{str(e)}")
        return xep, iq
