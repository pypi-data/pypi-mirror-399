#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# NOTE
# https://codeberg.org/poezio/slixmpp/src/branch/master/examples/download_avatars.py
# https://codeberg.org/poezio/slixmpp/src/branch/master/examples/set_avatar.py

from rivista.utility.logger import UtilityLogger
from slixmpp import Iq
from slixmpp.exceptions import IqError, IqTimeout
import sys

logger = UtilityLogger(__name__)

class InterfaceXmppAvatar:

    async def retrieve(xmpp_instance) -> Iq:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        jid_bare = xmpp_instance.boundjid.bare
        avatar = mime_type = None
        try:
            #iq = await xmpp_instance.plugin["xep_0084"].retrieve_avatar(jid_bare)
            iq = await xmpp_instance.plugin["xep_0054"].get_vcard(jid=jid_bare)
            iq_vcard_temp = iq['vcard_temp']
            avatar = iq_vcard_temp['PHOTO']['BINVAL']
            #mime_type = iq_vcard_temp['PHOTO']['TYPE']
        except (Exception, IqError, IqTimeout) as e:
            logger.error(f"{function_name}		{str(e)}")
        #return mime_type, avatar
        return avatar
