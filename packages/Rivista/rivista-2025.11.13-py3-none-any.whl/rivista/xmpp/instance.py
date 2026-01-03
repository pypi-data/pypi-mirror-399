#!/usr/bin/python
# -*- coding: utf-8 -*-

from slixmpp import ClientXMPP

class XmppInstance(ClientXMPP):
    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.register_plugin('xep_0060')
        self.connect()
        # self.process(forever=False)
