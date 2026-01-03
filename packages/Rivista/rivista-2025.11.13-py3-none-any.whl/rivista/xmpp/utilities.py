#!/usr/bin/python
# -*- coding: utf-8 -*-


class XmppUtilities:

    def form_a_node_link(pubsub, node):
        link = 'xmpp:{pubsub}?;node={node}'.format(pubsub=pubsub, node=node)
        return link
    
    def form_an_item_link(pubsub, node, item_id):
        link = 'xmpp:{pubsub}?;node={node};item={item}'.format(
            pubsub=pubsub, node=node, item=item_id)
        return link
