#!/usr/bin/python
# -*- coding: utf-8 -*-

from rivista.utility.logger import UtilityLogger
from slixmpp import ClientXMPP
import sys

logger = UtilityLogger(__name__)

class InterfaceXmppClient(ClientXMPP):

    def __init__(self, jid, password):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},{jid},Start")
        #super().__init__(jid, password)
        ClientXMPP.__init__(self, jid, password)

        # Event
        self.add_event_handler("changed_status", self.on_changed_status)
        self.add_event_handler("connection_failed", self.on_connection_failed)
        self.add_event_handler("failed_auth", self.on_failed_auth)
        self.add_event_handler("got_offline", self.on_got_offline)
        self.add_event_handler("session_start", self.on_session_start)

        # XEP
        self.register_plugin("xep_0004") # XEP-0004: Data Forms
        self.register_plugin("xep_0030") # XEP-0030: Service Discovery
        self.register_plugin("xep_0054") # XEP-0054: vcard-temp
        self.register_plugin("xep_0059") # XEP-0059: Result Set Management
        self.register_plugin("xep_0060") # XEP-0060: Publish-Subscribe
        self.register_plugin("xep_0078") # XEP-0078: Non-SASL Authentication
        self.register_plugin("xep_0163") # XEP-0163: Personal Eventing Protocol
        self.register_plugin("xep_0199") # XEP-0199: XMPP Ping
        self.register_plugin("xep_0223") # XEP-0223: Persistent Storage of Private Data via
        self.register_plugin("xep_0292") # XEP-0292: vCard4 Over XMPP PubSub
        self.connect()

    def on_changed_status(self, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},{event},Start")
        breakpoint()
        logger.debug(f"{function_name},{event},Finish")

    def on_connection_failed(self, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},{event},Start")
        self.is_connected = False
        logger.debug(f"{function_name},{event},Finish")

    def on_failed_auth(self, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},{event},Start")
        self.is_connected = False
        logger.debug(f"{function_name},{event},Finish")

    def on_got_offline(self, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},{event},Start")
        self.is_connected = False
        logger.debug(f"{function_name},{event},Finish")

    def on_session_start(self, event):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},{event},Start")
        self.is_connected = True
        logger.debug(f"{function_name},{event},Finish")
