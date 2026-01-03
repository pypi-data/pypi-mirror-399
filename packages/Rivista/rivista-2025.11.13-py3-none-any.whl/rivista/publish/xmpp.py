#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from rivista.compiler.atom import CompilerAtom
from rivista.interface.xmpp.client import InterfaceXmppClient
from rivista.interface.xmpp.iq import InsterfaceXmppIQ
from rivista.interface.xmpp.ping import InterfaceXmppPing
from rivista.interface.xmpp.pubsub import InsterfaceXmppPubsub
from rivista.parser.opml import ParserOpml
from rivista.parser.sitemap import ParserSitemap
from rivista.parser.toml import ParserToml
from rivista.parser.xml import ParserXml
from rivista.parser.xslt import ParserXslt
from rivista.property.publish import publish_properties
from rivista.utility.csv import UtilityCsv
from rivista.utility.document import UtilityDocument
from rivista.utility.html import UtilityHtml
from rivista.utility.logger import UtilityLogger
from rivista.utility.rst import UtilityRst
from rivista.utility.text import UtilityText
from rivista.utility.uri import UtilityUri
from rivista.utility.xml import UtilityXml
import sys

logger = UtilityLogger(__name__)

class PublishXmpp:

    async def initiate() -> None:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        address = publish_properties.address
        password = publish_properties.password
        xmpp_instance = InterfaceXmppClient(address, password)
        rtt = await InterfaceXmppPing.to_self(xmpp_instance)
        if xmpp_instance.is_connected or rtt:
            print("XMPP connectivity is established.")
            directory_source = publish_properties.directory_source
            # NOTE Iterate directories if PubSub (CMS), iterate directory "posts" if PEP.
            directory_source_posts = os.path.join(directory_source, "posts")
            jid = xmpp_instance.boundjid
            jid_bare = jid.bare
            node_name = "urn:xmpp:microblog:0"
            if not await InsterfaceXmppPubsub.is_node_exist(
                xmpp_instance, node_name):
                #result = await InsterfaceXmppPubsub.create_node(
                #    xmpp_instance, jid_bare, node_name)
                iq_create_node = InsterfaceXmppPubsub.create_node_atom(
                    xmpp_instance, jid_bare, node_name, "Journal", "Rivista Journal",
                    access_model="open", publish_model="open") # TODO Set value to "publishers".
                result = await InsterfaceXmppIQ.send(iq_create_node, 30)
            for filename in os.listdir(directory_source_posts):
                pathname = os.path.join(directory_source_posts, filename)
                if os.path.isfile(pathname):
                    atom_item = await PublishXmpp.page(
                        xmpp_instance, jid_bare, node_name, pathname,
                        directory_source_posts, filename)
                    payload_lxml = CompilerAtom.atomsub(atom_item)
                    payload_xml = UtilityXml.convert_lxml_to_xml(payload_lxml)
                    try:
                      iq = await InsterfaceXmppPubsub.publish_node_item(
                          xmpp_instance, jid_bare, node_name, atom_item["id"],
                          payload_xml)
                    except:
                      #breakpoint()
                      pass
            directory_xmpp = publish_properties.directory_xmpp
            if not os.path.exists(directory_xmpp): os.mkdir(directory_xmpp)
            """
            # Generate root files
            for filename in os.listdir(directory_source):
                pathname = os.path.join(directory_source, filename)
                if os.path.isfile(pathname):
                    PublishXmpp.page(pathname, filename)
            # Generate subsequent files
            for root, directories, filenames in os.walk(directory_source):
                for directory in directories:
                    pathname = os.path.join(root, directory)
                    directory_xmpp_directory = os.path.join(
                        publish_properties.directory_xmpp, directory)
                    if not os.path.exists(directory_xmpp_directory):
                        os.mkdir(directory_xmpp_directory)
                    index_file = os.path.join(pathname, "index.rst")
                    if not os.path.exists(index_file):
                        PublishXmpp.pages(pathname, directory)
                    for filename_ in os.listdir(pathname):
                        pathname_ = os.path.join(pathname, filename_)
                        if os.path.isfile(pathname_):
                            PublishXmpp.page(pathname_, filename_, directory)
                        elif os.path.isdir(pathname_):
                            print("Warning.")
            """
            #directory_source_posts = publish_properties.directory_source_posts
            #for filename in os.listdir(directory_source_posts):
            #    PublishXmpp.page(directory_source_posts, filename, "posts")
            #PublishXmpp.pages(directory_source_posts, "posts")

            #PublishXmpp.collection("collection.opml")
            #sitemap = ParserToml.open_file(publish_properties.sitemap_toml)
            #PublishXmpp.sitemap("sitemap.xml", sitemap, "sitemap")
            #for path in sitemap:
            #    PublishXmpp.sitemap(f"sitemap-{path}.xml", sitemap[path], "urlset")
            xmpp_instance.disconnect()
        else:
            print("Failed to connect to XMPP. Confirm account credentials validity.")
            #sys.exit(0)

    async def page(xmpp_instance, jid_bare, node_name, pathname, directory, filename) -> None:
        """Create an Atom Syndication Format with a single entry"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{pathname}	Start")
        rst_content_str = open(pathname, mode="r").read()
        lines = rst_content_str.split("\n")
        properties = UtilityRst.properties(rst_content_str)
        xhtml_content_str = UtilityDocument.convert(
          rst_content_str, "xhtml")
        comments_pubsub = publish_properties.comments
        item_id = properties["id"] or filename
        comments_node = f"{jid_bare}/{node_name}/{item_id}"
        uri_comments = (
            f"xmpp:{comments_pubsub}?;node={comments_node}")
        #if not await InsterfaceXmppPubsub.is_node_exist(
        #    xmpp_instance, comments_node):
        #result = await InsterfaceXmppPubsub.create_node(
        #    xmpp_instance, comments_pubsub, f"{comments_node}")
        iq_create_node = InsterfaceXmppPubsub.create_node_atom(
            xmpp_instance, jid_bare, node_name, "Journal", "Rivista Journal",
            access_model="open", publish_model="open")
        result = await InsterfaceXmppIQ.send(iq_create_node, 30)
        hostname_http = publish_properties.settings["domain-name"]["http"]
        # Generate Atom
        #link = "/"
        atom_item = {}
        atom_item["lang"] = properties["lang"] or publish_properties.locale
        atom_item["title"] = properties["title"]
        atom_item["links"] = [{
            # TODO Create an absolute XMPP URI.
            "href" : properties["link"],
            "rel" : "alternate",
            "title" : "",
            "type" : "application/xhtml+xml"}]
        properties_links = UtilityCsv.parse_csv_to_dict(properties["links"])
        for properties_link in properties_links:
            if "href" in properties_link:
                address = properties_link["href"]
                rel = properties_link["rel"] if "rel" in properties_link else ""
                title = properties_link["title"] if "title" in properties_link else ""
                mimetype = properties_link["type"] if "type" in properties_link else ""
                if not UtilityUri.has_scheme(address):
                    #breakpoint()
                    identifier = filename[:-4] if filename and filename != "index.rst" else ""
                    address = f"{hostname_http}/{directory}/{identifier}/{address}"
                atom_item["links"].append({
                    "href"   : address,
                    "length" : "", # TODO Filesize
                    "rel"    : rel,
                    "title"  : title,
                    "type"   : mimetype})
        atom_item["summary"] = properties["summary"]
        atom_item["content"] = {
            "text" : xhtml_content_str,
            "type" : "xhtml"}
        atom_item["published"] = properties["published"] if "published" in properties else ""
        atom_item["updated"] = properties["updated"]
        authors = properties["author"]
        if authors:
            atom_item["authors"] = []
            for author in authors.split("\n"):
                # TODO Create an absolute HTTP URL.
                author_properties = author.split(",")
                name = author_properties[0]
                address = author_properties[1] if len(author_properties) == 2 else ""
                atom_item["authors"].append({"name" : name.strip(),
                                             "address" : address.strip()})
        atom_item["id"] = properties["id"] or filename
        atom_item["categories"] = []
        properties_categories = properties["category"]
        if len(properties_categories.split("\n")) > 1:
            properties_categories = UtilityCsv.parse_csv_to_dict(properties_categories)
            for properties_category in properties_categories:
                term = properties_category["term"]
                label = properties_category["label"]
                if label or term:
                    if not term: term = label.lower()
                    scheme = properties_category["scheme"]
                    if scheme:
                        if UtilityUri.has_scheme(scheme):
                            address = scheme
                        else:
                            address = f"{hostname_http}/{scheme}"
                    else:
                        address = f"{hostname_http}/tag"
                    atom_item["categories"].append({
                        "scheme" : address,
                        "label"  : label,
                        "term"   : term})
        else:
            for tag in properties_categories.split(","):
                label = tag.strip()
                term = tag.lower().strip().replace(" ", "-")
                atom_item["categories"].append({
                    "term"   : term,
                    "label"  : label,
                    "scheme" : f"{hostname_http}/tag"})
        atom_item["links"].append({
            #"count" : "0",
            "href"  : uri_comments,
            "rel"   : "replies",
            "title" : "comments",
            "type"  : "application/atom+xml"})
        return atom_item
