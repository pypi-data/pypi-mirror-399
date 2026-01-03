#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from rivista.version import __version__
from rivista.xmpp.utilities import XmppUtilities
from slixmpp.stanza.iq import Iq
import xml.etree.ElementTree as ET

class XmlAtom:

    def error_message(text):
        """Error message in RFC 4287: The Atom Syndication Format."""
        title = "Rivista Voyager"
        subtitle = "XMPP Journal Publisher"
        description = ("This is a syndication feed generated with Rivista, an XMPP "
                       "Journal Publisher, which conveys XEP-0060: Publish-"
                       "Subscribe nodes to standard RFC 4287: The Atom Syndication "
                       "Format.")
        language = "en"
        feed = ET.Element("feed")
        feed.set("xmlns", "http://www.w3.org/2005/Atom")
        ET.SubElement(feed, "title", {"type": "text"}).text = title
        ET.SubElement(feed, "subtitle", {"type": "text"}).text = subtitle
        ET.SubElement(feed, "author", {"name":"Rivista","email":"rivista@schimon.i2p"})
        ET.SubElement(feed, "generator", {
            "uri": "https://git.xmpp-it.net/sch/Rivista",
            "version": f"{__version__}"}).text = "Rivista Voyager"
        ET.SubElement(feed, "updated").text = datetime.datetime.now(datetime.UTC).isoformat()
        entry = ET.SubElement(feed, "entry")
        ET.SubElement(entry, "title").text = "Error"
        ET.SubElement(entry, "id").text = "rivista-error"
        ET.SubElement(entry, "updated").text = datetime.datetime.now(datetime.UTC).isoformat()
        ET.SubElement(entry, "published").text = datetime.datetime.now(datetime.UTC).isoformat()
        # ET.SubElement(entry, "summary", {"type": summary_type_text}).text = summary_text
        ET.SubElement(entry, "content", {"type": "text"}).text = text
        return ET.tostring(feed, encoding="unicode")

    def extract_atom(iq: Iq):
        """Extract data from an Atom Syndication Format (RFC 4287) of a Publish-Subscribe (XEP-0060) node item."""
        jid = iq["from"].bare
        node = iq["pubsub"]["items"]["node"]
        atom = {}
        atom["title"] = jid
        atom["subtitle"] = node
        atom["language"] = iq["pubsub"]["items"]["lang"]
        atom["items"] = []
        items = iq["pubsub"]["items"]
        for item in list(items)[::-1]:
            atom_item = {}
            item_payload = item["payload"]
            namespace = "{http://www.w3.org/2005/Atom}"
            title = item_payload.find(namespace + "title")
            links = item_payload.find(namespace + "link")
            if (not isinstance(title, ET.Element) and
                not isinstance(links, ET.Element)): continue
            title_text = "No title" if title == None else title.text
            atom_item["title"] = title_text
            if isinstance(links, ET.Element):
                atom_item["links"] = []
                for link in item_payload.findall(namespace + "link"):
                    link_href = link.attrib["href"] if "href" in link.attrib else ""
                    link_type = link.attrib["type"] if "type" in link.attrib else ""
                    link_rel = link.attrib["rel"] if "rel" in link.attrib else ""
                    atom_item["links"].append({"href": link_href,
                                               "rel": link_rel,
                                               "type": link_type})
            contents = item_payload.find(namespace + "content")
            atom_item["contents"] = []
            if isinstance(contents, ET.Element):
                for content in item_payload.findall(namespace + "content"):
                    if not content.text: continue
                    content_text = content.text
                    content_type = content.attrib["type"] if "type" in content.attrib else "html"
                    content_type_text = "html" if "html" in content_type else "text"
                    atom_item["contents"].append({"text" : content_text,
                                                  "type" : content_type_text})
            else:
                summary = item_payload.find(namespace + "summary")
                summary_text = summary.text if summary else None
                if summary_text:
                    summary_type = summary.attrib["type"] if "type" in summary.attrib else "html"
                    summary_type_text = "html" if "html" in summary_type else "text"
                    atom_item["contents"].append(summary_text)
               # else:
               #     atom_item["contents"].append("No content.")
            published = item_payload.find(namespace + "published")
            published_text = "" if published == None else published.text
            atom_item["published"] = published_text
            updated = item_payload.find(namespace + "updated")
            updated_text = "" if updated == None else updated.text
            atom_item["updated"] = updated_text
            atom_item["authors"] = []
            authors = item_payload.find(namespace + "author")
            if isinstance(authors, ET.Element):
                for author in item_payload.findall(namespace + "author"):
                    atom_item_author = {}
                    author_email = author.find(namespace + "email")
                    if author_email is not None:
                        author_email_text = author_email.text
                        if author_email_text:
                            atom_item_author["email"] = author_email_text
                    else:
                        author_email_text = None
                    author_uri = author.find(namespace + "uri")
                    if author_uri is not None:
                        author_uri_text = author_uri.text
                        if author_uri_text:
                            atom_item_author["uri"] = author_uri_text
                    else:
                        author_uri_text = None
                    author_name = author.find(namespace + "name")
                    if author_name is not None and author_name.text:
                        author_name_text = author_name.text
                    else:
                        author_name_text = author_uri_text or author_email_text
                    atom_item_author["name"] = author_name_text
                    atom_item["authors"].append(atom_item_author)
            categories = item_payload.find(namespace + "category")
            atom_item["categories"] = []
            if isinstance(categories, ET.Element):
                for category in item_payload.findall(namespace + "category"):
                    if "term" in category.attrib and category.attrib["term"]:
                        category_term = category.attrib["term"]
                        atom_item["categories"].append(category_term)
            identifier = item_payload.find(namespace + "id")
            if identifier is not None and identifier.attrib: print(identifier.attrib)
            identifier_text = item["id"] if identifier == None else identifier.text
            atom_item["id"] = identifier_text
            #atom_item["id"] = item["id"]
            atom["items"].append(atom_item)
        return atom

    # generate_rfc_4287
    def generate_atom_post(atom: dict, pubsub: str, node: str, link: str):
        """Generate an Atom Syndication Format (RFC 4287) from a Publish-Subscribe (XEP-0060) node items."""
        # link = XmppUtilities.form_a_node_link(pubsub, node)
        # subtitle = "XMPP PubSub Syndication Feed"
        description = ("This is a syndication feed generated with Rivista, an XMPP "
                       "Journal Publisher, which conveys XEP-0060: Publish-"
                       "Subscribe nodes to standard RFC 4287: The Atom Syndication "
                       "Format.")
        e_feed = ET.Element("feed")
        e_feed.set("xmlns", "http://www.w3.org/2005/Atom")
        ET.SubElement(e_feed, "title", {"type": "text"}).text = atom["title"]
        ET.SubElement(e_feed, "subtitle", {"type": "text"}).text = atom["subtitle"]
        ET.SubElement(e_feed, "link", {"rel": "self", "href": link})
        ET.SubElement(e_feed, "generator", {
            "uri": "https://git.xmpp-it.net/sch/Rivista",
            "version": f"{__version__}"}).text = "Rivista Voyager"
        ET.SubElement(e_feed, "updated").text = datetime.datetime.now(datetime.UTC).isoformat()
        for item in atom["items"]:
            e_entry = ET.SubElement(e_feed, "entry")
            ET.SubElement(e_entry, "title").text = item["title"]
            links = item["links"] if "links" in item else None
            if links:
                for link in links:
                    ET.SubElement(e_entry, "link", {"href": link["href"],
                                                    "rel": link["rel"],
                                                    "type": link["type"]})
            else:
                # NOTE What does this instruction line do?
                ET.SubElement(e_entry, "content", {"href": ""})
            link_xmpp = XmppUtilities.form_an_item_link(pubsub, node, item["id"])
            ET.SubElement(e_entry, "link", {"href": link_xmpp,
                                            "rel": "alternate",
                                            "type": "x-scheme-handler/xmpp"})
            contents = item["contents"] if "contents" in item else None
            if contents:
                for content in contents:
                    ET.SubElement(e_entry, "content", {"type": content["type"]}).text = content["text"]
            else:
                ET.SubElement(e_entry, "content").text = "No content."
            ET.SubElement(e_entry, "published").text = item["published"]
            ET.SubElement(e_entry, "updated").text = item["updated"]
            authors = item["authors"] if "authors" in item else None
            if authors:
                for author in authors:
                    e_author = ET.SubElement(e_entry, "author")
                    if "email" in author and author["email"]:
                        ET.SubElement(e_author, "email").text = author["email"]
                    if "uri" in author and author["uri"]:
                        ET.SubElement(e_entry, "uri").text = author["uri"]
                        ET.SubElement(e_author, "uri").text = author["uri"]
                    ET.SubElement(e_author, "name").text = author["name"] or author["uri"] or author["email"]
            categories = item["categories"]
            if categories:
                for category in categories:
                    ET.SubElement(e_entry, "category", {"term": category})

            ET.SubElement(e_entry, "id").text = item["id"]
        return ET.tostring(e_feed, encoding="unicode")

    # generate_rfc_4287
    def generate_atom_comment(atom: dict, pubsub: str, node: str, link: str):
        """Generate an Atom Syndication Format (RFC 4287) from a Publish-Subscribe (XEP-0060) node items."""
        # link = XmppUtilities.form_a_node_link(pubsub, node)
        # subtitle = "XMPP PubSub Syndication Feed"
        description = ("This is a syndication feed generated with Rivista, an XMPP "
                       "Journal Publisher, which conveys XEP-0060: Publish-"
                       "Subscribe nodes to standard RFC 4287: The Atom Syndication "
                       "Format.")
        e_feed = ET.Element("feed")
        e_feed.set("xmlns", "http://www.w3.org/2005/Atom")
        ET.SubElement(e_feed, "title", {"type": "text"}).text = atom["title"]
        ET.SubElement(e_feed, "subtitle", {"type": "text"}).text = atom["subtitle"]
        ET.SubElement(e_feed, "link", {"rel": "self", "href": link})
        ET.SubElement(e_feed, "generator", {
            "uri": "https://git.xmpp-it.net/sch/Rivista",
            "version": f"{__version__}"}).text = "Rivista Voyager"
        ET.SubElement(e_feed, "updated").text = datetime.datetime.now(datetime.UTC).isoformat()
        for item in atom["items"]:
            e_entry = ET.SubElement(e_feed, "entry")
            ET.SubElement(e_entry, "title").text = item["authors"][0]["name"]
            links = item["links"] if "links" in item else None
            if links:
                for link in links:
                    ET.SubElement(e_entry, "link", {"href": link["href"],
                                                    "rel": link["rel"],
                                                    "type": link["type"]})
            else:
                # NOTE What does this instruction line do?
                ET.SubElement(e_entry, "content", {"href": ""})
            link_xmpp = XmppUtilities.form_an_item_link(pubsub, node, item["id"])
            ET.SubElement(e_entry, "link", {"href": link_xmpp,
                                            "rel": "alternate",
                                            "type": "x-scheme-handler/xmpp"})
            contents = item["contents"] if "contents" in item else None
            if contents:
                for content in contents:
                    ET.SubElement(e_entry, "content", {"type": content["type"]}).text = content["text"]
            else:
                ET.SubElement(e_entry, "content").text = "No content."
            ET.SubElement(e_entry, "published").text = item["published"]
            ET.SubElement(e_entry, "updated").text = item["updated"]
            authors = item["authors"] if "authors" in item else None
            if authors:
                for author in authors:
                    e_author = ET.SubElement(e_entry, "author")
                    if "email" in author and author["email"]:
                        ET.SubElement(e_author, "email").text = author["email"]
                    if "uri" in author and author["uri"]:
                        ET.SubElement(e_entry, "uri").text = author["uri"]
                        ET.SubElement(e_author, "uri").text = author["uri"]
                    ET.SubElement(e_author, "name").text = author["name"] or author["uri"] or author["email"]
            categories = item["categories"]
            if categories:
                for category in categories:
                    ET.SubElement(e_entry, "category", {"term": category})

            ET.SubElement(e_entry, "id").text = item["id"]
        return ET.tostring(e_feed, encoding="unicode")
