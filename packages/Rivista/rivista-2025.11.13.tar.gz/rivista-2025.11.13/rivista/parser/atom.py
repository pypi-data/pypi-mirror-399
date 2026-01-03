#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from slixmpp.stanza.iq import Iq
from rivista.utility.logger import UtilityLogger
from rivista.version import __version__
import sys
import xml.etree.ElementTree as XET
import lxml.etree as ET

logger = UtilityLogger(__name__)

class ParserAtom:

    # TODO Replace function "atomsub" in favour of function "activity_stream",
    # and externally iterate IQ items.
    def activity_stream(item_payload, limit=False):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        xmlns = "{http://www.w3.org/2005/Atom}"
        title = item_payload.find(xmlns + "title")
        links = item_payload.find(xmlns + "link")
        if (not isinstance(title, ET.Element) and
            not isinstance(links, ET.Element)): return None
        title_text = "" if title == None else title.text
        if isinstance(links, ET.Element):
            for link in item_payload.findall(xmlns + "link"):
                link_href = link.attrib["href"] if "href" in link.attrib else ""
                if link_href: break
        contents = item_payload.find(xmlns + "summary")
        summary_text = ""
        if isinstance(contents, ET.Element):
            for summary in item_payload.findall(xmlns + "summary"):
                summary_text = summary.text or ""
                if summary_text: break
        published = item_payload.find(xmlns + "published")
        published_text = "" if published == None else published.text
        categories = item_payload.find(xmlns + "category")
        tags = []
        if isinstance(categories, ET.Element):
            for category in item_payload.findall(xmlns + "category"):
                if "term" in category.attrib and category.attrib["term"]:
                    category_term = category.attrib["term"]
                    if len(category_term) < 20:
                        tags.append(category_term)
                    elif len(category_term) < 50:
                        tags.append(category_term)
                    if limit and len(tags) > 4: break
        identifier = item_payload.find(xmlns + "id")
        if identifier and identifier.attrib: print(identifier.attrib)
        identifier_text = "" if identifier == None else identifier.text
        instances = "" # TODO Check the Blasta database for instances.
        entry = {"title" : title_text,
                 "link" : link_href,
                 "summary" : summary_text,
                 "published" : published_text,
                 "updated" : published_text, # TODO "Updated" is missing
                 "tags" : tags}
        return entry

    def atomsub(iq: Iq):
        """
        Extract data from a set of entries of Atom Over XMPP
        (Atomsub) of a PubSub (Publish-Subscribe) node item.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        jid = iq["from"].bare
        node = iq["pubsub"]["items"]["node"]
        atom = {}
        atom["title"] = jid
        atom["subtitle"] = node
        atom["language"] = iq["pubsub"]["items"]["lang"]
        atom["items"] = []
        items = iq["pubsub"]["items"]
        items_list = list(items)
        items_list.reverse()
        for item in items_list:
        #for item in list(items)[::-1]:
            atom_item = {}
            item_payload = item["payload"]
            xmlns = "{http://www.w3.org/2005/Atom}"
            title = item_payload.find(xmlns + "title")
            links = item_payload.find(xmlns + "link")
            if (not isinstance(title, ET.Element) and
                not isinstance(links, ET.Element)): continue
            title_text = "No title" if title == None else title.text
            atom_item["title"] = title_text
            if isinstance(links, ET.Element):
                atom_item["links"] = []
                for link in item_payload.findall(xmlns + "link"):
                    link_href = link.attrib["href"] if "href" in link.attrib else ""
                    link_type = link.attrib["type"] if "type" in link.attrib else ""
                    link_rel = link.attrib["rel"] if "rel" in link.attrib else ""
                    atom_item["links"].append({"href" : link_href,
                                               "rel"  : link_rel,
                                               "type" : link_type})
            contents = item_payload.find(xmlns + "content")
            atom_item["contents"] = []
            if isinstance(contents, ET.Element):
                for content in item_payload.findall(xmlns + "content"):
                    if not content.text: continue
                    content_text = content.text
                    content_type = content.attrib["type"] if "type" in content.attrib else "html"
                    content_type_text = "html" if "html" in content_type else "text"
                    atom_item["contents"].append({"text" : content_text,
                                                  "type" : content_type_text})
            else:
                summary = item_payload.find(xmlns + "summary")
                summary_text = summary.text if summary else None
                if summary_text:
                    summary_type = summary.attrib["type"] if "type" in summary.attrib else "html"
                    summary_type_text = "html" if "html" in summary_type else "text"
                    atom_item["contents"].append(summary_text)
               # else:
               #     atom_item["contents"].append("No content.")
            published = item_payload.find(xmlns + "published")
            published_text = "" if published == None else published.text
            atom_item["published"] = published_text
            updated = item_payload.find(xmlns + "updated")
            updated_text = "" if updated == None else updated.text
            atom_item["updated"] = updated_text
        for people in ("author", "contributor"):
            atom_item[people] = []
            peoples = item_payload.find(xmlns + people)
            if isinstance(peoples, ET.Element):
                for people in item_payload.findall(xmlns + people):
                    atom_item_people = {}
                    people_email = people.find(xmlns + "email")
                    if people_email is not None:
                        people_email_text = people_email.text
                        if people_email_text:
                            atom_item_people["email"] = people_email_text
                    else:
                        people_email_text = None
                    people_uri = people.find(xmlns + "uri")
                    if people_uri is not None:
                        people_uri_text = people_uri.text
                        if people_uri_text:
                            atom_item_people["uri"] = people_uri_text
                    else:
                        people_uri_text = None
                    people_name = people.find(xmlns + "name")
                    if people_name is not None and people_name.text:
                        people_name_text = people_name.text
                    else:
                        people_name_text = people_uri_text or people_email_text
                    atom_item_people["name"] = people_name_text
                    atom_item[people].append(atom_item_people)
            categories = item_payload.find(xmlns + "category")
            atom_item["categories"] = []
            if isinstance(categories, ET.Element):
                for category in item_payload.findall(xmlns + "category"):
                    if "term" in category.attrib and category.attrib["term"]:
                        category_term = category.attrib["term"]
                        atom_item["categories"].append(category_term)
            identifier = item_payload.find(xmlns + "id")
            if identifier is not None and identifier.attrib: print(identifier.attrib)
            identifier_text = item["id"] if identifier == None else identifier.text
            atom_item["id"] = identifier_text
            #atom_item["id"] = item["id"]
            atom["items"].append(atom_item)
        return atom

    def extract_element_link(filename, relation):
        """
        Retrieve instances of element link of a given relation (attribute "rel")
        from an Atom Syndication Format.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        document = ET.parse(filename)
        xmlns = "{http://www.w3.org/2005/Atom}"
        return document.findall(xmlns + "link[@rel='" + relation + "']")

