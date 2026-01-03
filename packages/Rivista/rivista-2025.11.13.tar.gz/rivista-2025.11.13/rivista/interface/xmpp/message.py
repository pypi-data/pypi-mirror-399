#!/usr/bin/python
# -*- coding: utf-8 -*-

from rivista.utility.logger import UtilityLogger
#from slixmpp.exceptions import IqError, IqTimeout
import sys

logger = UtilityLogger(__name__)

class InterfaceXmppMessage:

    def send(self, jid, message_body):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        jid_from = str(self.boundjid) if self.is_component else None
        self.send_message(
            mto=jid,
            mfrom=jid_from,
            mbody=message_body,
            mtype='chat')

    # NOTE It appears to not work.
    def send_headline(self, jid, message_subject, message_body):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f'{function_name},,Start')
        jid_from = str(self.boundjid) if self.is_component else None
        self.send_message(
            mto=jid,
            mfrom=jid_from,
            msubject=message_subject,
            mbody=message_body,
            mtype='headline')
