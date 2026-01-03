#!/usr/bin/python
# -*- coding: utf-8 -*-

from rivista.utility.logger import UtilityLogger
from slixmpp.exceptions import IqError, IqTimeout
#import slixmpp.plugins.xep_0060.stanza.pubsub as pubsub
import slixmpp.plugins.xep_0059.rsm as rsm
import sys

logger = UtilityLogger(__name__)

class InsterfaceXmppPubsub:

    async def create_node(xmpp_instance, jid, node, config=None, ntype=None,
                    ifrom=None, callback=None, timeout=None):
        try:
            iq = await xmpp_instance.plugin['xep_0060'].create_node(
                jid, node, config, ntype, ifrom, callback, timeout)
            result = iq
        except IqError as e:
            result = e.iq['error']['text']
            print(e)
        except IqTimeout as e:
            result = 'Timeout'
            print(e)
        print(result)
        return result

    # TODO max-items might be limited (CanChat: 255), so iterate from a bigger number to a smaller.
    # NOTE This function was copied from atomtopubsub
    def create_node_atom(xmpp_instance, jid, node, title, subtitle,
                         access_model="open", publish_model="publishers"):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        #jid_from = xmpp_instance.boundjid.full if xmpp_instance.is_component else None
        jid_from = xmpp_instance.boundjid.full
        iq = xmpp_instance.Iq(stype="set",
                              sto=jid,
                              sfrom=jid_from)
        iq["pubsub"]["create"]["node"] = node
        form = iq["pubsub"]["configure"]["form"]
        form["type"] = "submit"
        form.addField("pubsub#access_model",
                      ftype="list-single",
                      value=access_model)
        form.addField("pubsub#deliver_payloads",
                      ftype="boolean",
                      value=0)
        form.addField("pubsub#description",
                      ftype="text-single",
                      value=subtitle)
        form.addField("pubsub#max_items",
                      ftype="text-single",
                      value="255")
        form.addField("pubsub#notify_retract",
                      ftype="boolean",
                      value=1)
        form.addField("pubsub#persist_items",
                      ftype="boolean",
                      value=1)
        form.addField("pubsub#publish_model",
                      ftype="boolean",
                      value=publish_model)
        form.addField("pubsub#send_last_published_item",
                      ftype="text-single",
                      value="never")
        form.addField("pubsub#title",
                      ftype="text-single",
                      value=title)
        form.addField("pubsub#type",
                      ftype="text-single",
                      value="http://www.w3.org/2005/Atom")
        return iq

    def create_node_config(xmpp_instance, jid, node_settings_id):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        #jid_from = xmpp_instance.boundjid.full if xmpp_instance.is_component else None
        jid_from = xmpp_instance.boundjid.full
        iq = xmpp_instance.Iq(stype="set",
                              sto=jid,
                              sfrom=jid_from)
        iq["pubsub"]["create"]["node"] = node_settings_id
        form = iq["pubsub"]["configure"]["form"]
        form["type"] = "submit"
        form.addField("pubsub#access_model",
                      ftype="list-single",
                      value="whitelist")
        form.addField("pubsub#deliver_payloads",
                      ftype="boolean",
                      value=0)
        form.addField("pubsub#description",
                      ftype="text-single",
                      value="Settings of the Rivista publishing system")
        form.addField("pubsub#max_items",
                      ftype="text-single",
                      value="30")
        form.addField("pubsub#notify_retract",
                      ftype="boolean",
                      value=1)
        form.addField("pubsub#persist_items",
                      ftype="boolean",
                      value=1)
        form.addField("pubsub#send_last_published_item",
                      ftype="text-single",
                      value="never")
        form.addField("pubsub#title",
                      ftype="text-single",
                      value="Rivista Settings")
        form.addField("pubsub#type",
                      ftype="text-single",
                      value="settings")
        return iq

    async def del_node_item(xmpp_instance, pubsub, node, item_id):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        try:
            iq = await xmpp_instance.plugin["xep_0060"].retract(
                pubsub, node, item_id, timeout=5, notify=None)
            result = iq
        except IqError as e:
            result = e.iq["error"]["text"]
            print(e)
        except IqTimeout as e:
            result = "Timeout"
            print(e)
        print(result)
        return result
    
    def get_iterator(xmpp_instance, pubsub, node, max_items, iterator):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        iterator = xmpp_instance.plugin["xep_0060"].get_items(
            pubsub, node, timeout=5, max_items=max_items, iterator=iterator)
        return iterator

    async def get_node_configuration(xmpp_instance, pubsub, node):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        try:
          iq = await xmpp_instance.plugin["xep_0060"].get_node_config(
              pubsub, node)
          return iq
        except (IqError, IqTimeout) as e:
          print(e)

    async def get_node_item(xmpp_instance, pubsub, node, item_id):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        try:
            iq = await xmpp_instance.plugin["xep_0060"].get_item(
                pubsub, node, item_id, timeout=5)
            result = iq
        except IqError as e:
            result = e.iq["error"]["text"]
            print(e)
        except IqTimeout as e:
            result = "Timeout"
            print(e)
        return result

    async def get_node_item_ids(xmpp_instance, pubsub, node):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        try:
            iq = await xmpp_instance.plugin["xep_0030"].get_items(
                pubsub, node)
            # Broken. See https://codeberg.org/poezio/slixmpp/issues/3548
            #iq = await xmpp_instance.plugin["xep_0060"].get_item_ids(
            #    pubsub, node, timeout=5)
            result = iq
        except IqError as e:
            if e.iq["error"]["text"] == "Node not found":
                result = "Node not found"
            elif e.iq["error"]["condition"] == "item-not-found":
                result = "Item not found"
            else:
                result = None
            print(e)
        except IqTimeout as e:
            result = "Timeout"
            print(e)
        return result

    async def get_node_item_private(xmpp_instance, node, item_id):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        try:
            iq = await xmpp_instance.plugin["xep_0223"].retrieve(
                node, item_id, timeout=5)
            result = iq
        except IqError as e:
            result = e.iq["error"]["text"]
            print(e)
        except IqTimeout as e:
            result = "Timeout"
            print(e)
        return result
    
    async def get_node_items(xmpp_instance, pubsub, node, item_ids=None, max_items=None):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        try:
            if max_items:
                iq = await xmpp_instance.plugin["xep_0060"].get_items(
                    pubsub, node, timeout=5)
                it = xmpp_instance.plugin["xep_0060"].get_items(
                    pubsub, node, timeout=5, max_items=max_items, iterator=True)
                q = rsm.Iq()
                q["to"] = pubsub
                q["disco_items"]["node"] = node
                async for item in rsm.ResultIterator(q, "disco_items", "10"):
                    print(item["disco_items"]["items"])

            else:
                iq = await xmpp_instance.plugin["xep_0060"].get_items(
                    pubsub, node, timeout=5, item_ids=item_ids)
            result = iq
        except IqError as e:
            if e.iq["error"]["text"] == "Node not found":
                result = "Node not found"
            elif e.iq["error"]["condition"] == "item-not-found":
                result = "Item not found"
            else:
                result = None
            print(e)
        except IqTimeout as e:
            result = "Timeout"
            print(e)
        return result

    async def get_nodes(xmpp_instance):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        try:
          iq = await xmpp_instance.plugin["xep_0060"].get_nodes()
          return iq
        except (IqError, IqTimeout) as e:
          print(e)

    async def is_node_exist(xmpp_instance, node_name):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        iq = await InsterfaceXmppPubsub.get_nodes(xmpp_instance)
        nodes = iq["disco_items"]["items"]
        for node in nodes:
            if node[1] == node_name:
                return True

    async def publish_node_item(xmpp_instance, jid_bare, node_name, item_id, payload):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        try:
          iq = await xmpp_instance.plugin["xep_0060"].publish(
                jid_bare, node_name, id=item_id, payload=payload)
          print(iq)
          return iq
        except (IqError, IqTimeout) as e:
          print(e)

    async def publish_node_item_private(xmpp_instance, node_name, item_id, stanza):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        try:
          iq = await xmpp_instance.plugin["xep_0223"].store(
                stanza, node_name, item_id)
          print(iq)
          return iq
        except (IqError, IqTimeout) as e:
          print(e)
          if e.iq["error"]["text"] == "Field does not match: access_model":
              return "Error: Could not set private bookmark due to Access Model mismatch"

    async def set_node_private(xmpp_instance, node_name):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name},,Start")
        try:
          iq = await xmpp_instance.plugin["xep_0223"].configure(node_name)
          print(iq)
          return iq
        except (IqError, IqTimeout) as e:
          print(e)
