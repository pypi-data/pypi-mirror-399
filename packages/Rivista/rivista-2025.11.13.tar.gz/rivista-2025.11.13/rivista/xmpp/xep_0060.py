#!/usr/bin/python
# -*- coding: utf-8 -*-

from slixmpp.exceptions import IqError, IqTimeout

class XmppXep0060:

    async def get_node_item(self, pubsub, node, item_id):
        try:
          iq = await self.plugin['xep_0060'].get_item(pubsub, node, item_id, timeout=5)
          return iq
        except (IqError, IqTimeout) as e:
          print(e)

    async def get_node_items(self, pubsub, node):
        try:
          iq = await self.plugin['xep_0060'].get_items(pubsub, node, timeout=5)
          return iq
        except (IqError, IqTimeout) as e:
          print(e)

    async def get_nodes(self, pubsub):
        try:
          iq = await self.plugin['xep_0060'].get_nodes(pubsub, timeout=5)
          return iq
        except (IqError, IqTimeout) as e:
          print(e)
