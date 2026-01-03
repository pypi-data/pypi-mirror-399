#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from rivista.xmpp.utilities import XmppUtilities
import xml.etree.ElementTree as ET

class XmlOpml:

    def generate_opml(iq):
        """Generate an OPML Collection document."""
        pubsub = iq['from'].bare
        items = iq['disco_items']['items']
        opml = ET.Element("opml")
        opml.set("version", "1.0")
        head = ET.SubElement(opml, "head")
        ET.SubElement(head, "title").text = 'An OPML of ' + pubsub
        ET.SubElement(head, "description").text = (
            "PubSub Nodes of {}").format(pubsub)
        ET.SubElement(head, "generator").text = 'Rivista'
        ET.SubElement(head, "urlPublic").text = 'https://git.xmpp-it.net/sch/Rivista'
        time_stamp = datetime.datetime.now(datetime.UTC).isoformat()
        ET.SubElement(head, "dateCreated").text = time_stamp
        ET.SubElement(head, "dateModified").text = time_stamp
        body = ET.SubElement(opml, "body")
        for item in items:
            pubsub, node, title = item
            uri = XmppUtilities.form_a_node_link(pubsub, node)
            outline = ET.SubElement(body, "outline")
            outline.set("text", title or node)
            outline.set("xmlUrl", uri)
        return ET.tostring(opml, encoding='unicode')
