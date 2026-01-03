#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from slixmpp.stanza.iq import Iq
from rivista.utility.logger import UtilityLogger
from rivista.version import __version__
import sys
import lxml.etree as ET

logger = UtilityLogger(__name__)

class CompilerAtom:

    def atomsub(atom_entry):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        #e_entry = ET.Element("entry")
        #e_entry.set("xmlns", "http://www.w3.org/2005/Atom")
        
        e_entry = ET.Element("entry",
            attrib={
                #"{http://www.w3.org/XML/1998/namespace}base" : "",
                "{http://www.w3.org/XML/1998/namespace}lang" : atom_entry["lang"]},
            nsmap={
                None        : "http://www.w3.org/2005/Atom",
                "activity"  : "http://activitystrea.ms/spec/1.0/",
                "atommedia" : "http://purl.org/syndication/atommedia",
                "atompub"   : "http://purl.org/atompub/tombstones/1.0",
                "dfrn"      : "http://purl.org/macgirvin/dfrn/1.0",
                "ostatus"   : "http://ostatus.org/schema/1.0",
                #"thr"      : "http://purl.org/syndication/thread/1.0",
                #"xhtml"    : "http://www.w3.org/1999/xhtml",
                "xlink"     : "http://www.w3.org/1999/xlink",
                "xml"       : "http://www.w3.org/XML/1998/namespace"})
        
        # Title
        title = ET.SubElement(e_entry, "title")
        title.set("type", "text")
        title.text = atom_entry["title"]
        # Summary
        summary = ET.SubElement(e_entry, "summary")
        summary.set("type", "text")
        #summary.set("lang", atom_entry["summary_lang"])
        summary.text = atom_entry["summary"]
        # Content
        #content.set("lang", atom_entry["content_lang"])
        e_content = ET.SubElement(e_entry, "content", {
            "type" : atom_entry["content"]["type"]})
        element_xhtml = ET.HTML(atom_entry["content"]["text"])

        # Extract element "main"; add attribute "xmlns" and rename tag to "div".
        element_content = element_xhtml.xpath("//main")[0]
        element_content.tag = "div"
        element_content.attrib["xmlns"] = "http://www.w3.org/1999/xhtml"

        # Remove all comment nodes.
        elements_comment = element_xhtml.xpath("//comment()")
        for element_comment in elements_comment:
            element_comment.getparent().remove(element_comment)
        e_content.append(element_content)
        # Tags
        categories = atom_entry["categories"]
        for category in categories:
            ET.SubElement(e_entry, "category", {
                "term": category["term"],
                "label": category["label"],
                "scheme": category["scheme"]})
        # Links
        for atom_entry_link in atom_entry["links"]:
            href = atom_entry_link["href"] if "href" in atom_entry_link else ""
            mimetype = atom_entry_link["type"] if "type" in atom_entry_link else ""
            rel = atom_entry_link["rel"] if "rel" in atom_entry_link else ""
            title = atom_entry_link["title"] if "title" in atom_entry_link else ""
            link = ET.SubElement(e_entry, "link")
            if title: link.set("title", title)
            if href: link.set("href", href)
            if mimetype: link.set("type", mimetype)
            if rel: link.set("rel", rel)
        # Date saved
        if "published" in atom_entry and atom_entry["published"]:
            published = ET.SubElement(e_entry, "published")
            published.text = atom_entry["published"]
        # Date edited
        if "updated" in atom_entry and atom_entry["updated"]:
            updated = ET.SubElement(e_entry, "updated")
            updated.text = atom_entry["updated"]
        return e_entry

    # NOTE Activity Streams be implemented only to comments (a single comment
    #      entry), due to the need of element "atom:source" (external data).
    # TODO Add "avatar" and "photo" as element "atom:link[@rel='photo']";
    #      Add "icon" and "logo" as element "atom:link[@rel='logo']"; and
    #      Add element "atom:generator".
    def activity_stream(atom_entry: dict, filepath_xslt: str):
        """
        Generate an Atom Activity Stream document from a given dictionary.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        locale = atom_entry["lang"]
        e_entry = ET.Element("entry",
            attrib={
                #"{http://www.w3.org/XML/1998/namespace}base" : "",
                "{http://www.w3.org/XML/1998/namespace}lang" : locale},
            nsmap={
                None        : "http://www.w3.org/2005/Atom",
                "activity"  : "http://activitystrea.ms/spec/1.0/",
                "atommedia" : "http://purl.org/syndication/atommedia",
                "atompub"   : "http://purl.org/atompub/tombstones/1.0",
                "dfrn"      : "http://purl.org/macgirvin/dfrn/1.0",
                "ostatus"   : "http://ostatus.org/schema/1.0",
                #"thr"      : "http://purl.org/syndication/thread/1.0",
                #"xhtml"    : "http://www.w3.org/1999/xhtml",
                "xlink"     : "http://www.w3.org/1999/xlink",
                "xml"       : "http://www.w3.org/XML/1998/namespace"})
        ET.SubElement(e_entry, "title").text = atom_entry["title"]
        links = atom_entry["links"] if "links" in atom_entry else None
        if links:
            thread_count = None
            for link in links:
                if "count" in link:
                    thread_count = link["count"]
                    ET.SubElement(e_entry, "link", {
                        "href"  : link["href"],
                        "rel"   : link["rel"],
                        "title" : link["title"],
                        "type"  : link["type"],
                        "{http://purl.org/syndication/thread/1.0}count" : link["count"]})
                else:
                    ET.SubElement(e_entry, "link", {
                        "href"  : link["href"],
                        "rel"   : link["rel"],
                        "title" : link["title"],
                        "type"  : link["type"]})
            if thread_count:
                e_thread = ET.SubElement(
                    e_entry, "{http://purl.org/syndication/thread/1.0}total")
                e_thread.text = thread_count
        ET.SubElement(e_entry, "published").text = atom_entry["published"]
        ET.SubElement(e_entry, "updated").text = atom_entry["updated"]
        for people in ("author", "contributor"):
            peoples = atom_entry[people] if people in atom_entry else None
            if peoples:
                for peopled in peoples:
                    e_people = ET.SubElement(e_entry, people)
                    if "email" in peopled and peopled["email"]:
                        ET.SubElement(e_people, "email").text = peopled["email"]
                    if "uri" in peopled and peopled["uri"]:
                        ET.SubElement(e_people, "uri").text = peopled["uri"]
                    ET.SubElement(e_people, "name").text = peopled["name"]
        if "rights" in atom_entry and atom_entry["rights"]:
            ET.SubElement(e_entry, "rights").text = atom_entry["rights"]
        summary = atom_entry["summary"]
        if summary:
            summaryd = {
                "type" : "text",
                "text" : atom_entry["summary"],
                "link" : ""}
            ET.SubElement(e_entry, "summary", {
                "type": summaryd["type"]}).text = summaryd["text"]
        content = atom_entry["content"] if "content" in atom_entry else None
        if content:
            e_content = ET.SubElement(e_entry, "content", {
                "type"  : content["type"]})
            # FIXME Invalid XML.
            #       This could be an issue of Docutils
            #       Function "publish_parts", option "fragment".
            #element_xhtml = ET.fromstring(content["text"])
            element_xhtml = ET.HTML(content["text"])

            # TODO Remove elements html, body, and main; and comment nodes.
            #elements = element_xhtml.xpath("//*")
            #elements.reverse()
            #for element in elements: element.getparent().remove(element)

            #if not element_xhtml:
            #    element_xhtml = ET.fromstring(
            #        content["text"], parser=ET.XMLParser(recover=True))

            #c_div = ET.SubElement(e_content, "div", {
            #    "xhtml" : "http://www.w3.org/1999/xhtml"})
            #c_div.append(element_xhtml)

            # Extract element "main"; add attribute "xmlns" and rename tag to "div".
            element_content = element_xhtml.xpath("//main")[0]
            element_content.tag = "div"
            element_content.attrib["xmlns"] = "http://www.w3.org/1999/xhtml"

            # Remove all comment nodes.
            elements_comment = element_xhtml.xpath("//comment()")
            for element_comment in elements_comment:
                element_comment.getparent().remove(element_comment)

            e_content.append(element_content)

            #element_xhtml = ET.fromstring(
            #    "<div xmlns:xhtml=\"http://www.w3.org/1999/xhtml\">" +
            #    content["text"] +
            #    "</div>", parser=ET.XMLParser(recover=True))
            #e_content.append(element_xhtml)
        categories = atom_entry["categories"]
        if categories:
            for category in categories:
                ET.SubElement(e_entry, "category", {
                    "term": category["term"],
                    "label": category["label"],
                    "scheme": category["scheme"]})

            ET.SubElement(e_entry, "id").text = atom_entry["id"]
        xslt_reference = ET.ProcessingInstruction(
            "xml-stylesheet",
            f"type=\"text/xml\" href=\"{filepath_xslt}\"")
        e_entry.addprevious(xslt_reference)
        xml_data = ET.ElementTree(e_entry)
        xml_data_bytes = ET.tostring(
            xml_data,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8")
        xml_data_str = xml_data_bytes.decode("utf-8")
        return xml_data_str

    def syndication_format(atom: dict, filepath_xslt: str):
        """
        Generate an Atom Syndication Format document from a given dictionary.
        """
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        locale = atom["lang"]
        e_feed = ET.Element("feed",
            attrib={
                #"{http://www.w3.org/XML/1998/namespace}base" : "",
                "{http://www.w3.org/XML/1998/namespace}lang" : locale},
            nsmap={
                None    : "http://www.w3.org/2005/Atom",
                #"thr"   : "http://purl.org/syndication/thread/1.0",
                #"xhtml" : "http://www.w3.org/1999/xhtml",
                "xlink" : "http://www.w3.org/1999/xlink",
                "xml"   : "http://www.w3.org/XML/1998/namespace"})
        if "icon" in atom: ET.SubElement(e_feed, "icon").text = atom["icon"]
        if "logo" in atom: ET.SubElement(e_feed, "logo").text = atom["logo"]
        ET.SubElement(e_feed, "title", {"type": "text"}).text = atom["title"]
        ET.SubElement(e_feed, "subtitle", {"type": "text"}).text = atom["subtitle"]
        atom_categories = atom["categories"] if "categories" in atom else []
        if atom_categories:
            for atom_category in atom_categories:
                ET.SubElement(e_feed, "category", {
                   "term": atom_category["term"],
                   "label": atom_category["label"],
                   "scheme": atom_category["scheme"]})
        ET.SubElement(e_feed, "rights").text = atom["rights"]
        if "summary" in atom and atom["summary"]:
            ET.SubElement(e_feed, "summary", {
                "type": atom["summary"]["type"]}).text = atom["summary"]["text"]
        if "links" in atom:
            for link in atom["links"]:
                ET.SubElement(e_feed, "link", {
                    "href"  : link["href"],
                    "rel"   : link["rel"],
                    "title" : link["title"],
                    "type"  : link["type"]})
        e_generator = ET.SubElement(e_feed, "generator", {
            "uri"    : "https://git.xmpp-it.net/sch/Rivista",
            "version": f"{__version__}"})
        e_generator.text = "Rivista Voyager"
        ET.SubElement(e_feed, "updated").text = datetime.datetime.now(datetime.UTC).isoformat()
        for item in atom["items"]:
            e_entry = ET.SubElement(e_feed, "entry")
            ET.SubElement(e_entry, "title").text = item["title"]
            links = item["links"] if "links" in item else None
            if links:
                thread_count = None
                for link in links:
                    if "count" in link:
                        thread_count = link["count"]
                        ET.SubElement(e_entry, "link", {
                            "href"  : link["href"],
                            "rel"   : link["rel"],
                            "title" : link["title"],
                            "type"  : link["type"],
                            "{http://purl.org/syndication/thread/1.0}count" : link["count"]})
                    else:
                        ET.SubElement(e_entry, "link", {
                            "href"  : link["href"],
                            "rel"   : link["rel"],
                            "title" : link["title"],
                            "type"  : link["type"]})
                if thread_count:
                    e_thread = ET.SubElement(
                        e_entry, "{http://purl.org/syndication/thread/1.0}total")
                    e_thread.text = thread_count
            ET.SubElement(e_entry, "published").text = item["published"]
            ET.SubElement(e_entry, "updated").text = item["updated"]
            for people in ("author", "contributor"):
                peoples = item[people] if people in item else None
                if peoples:
                    for peopled in peoples:
                        e_people = ET.SubElement(e_entry, people)
                        if "email" in peopled and peopled["email"]:
                            ET.SubElement(e_people, "email").text = peopled["email"]
                        if "uri" in peopled and peopled["uri"]:
                            ET.SubElement(e_people, "uri").text = peopled["uri"]
                        ET.SubElement(e_people, "name").text = peopled["name"]
            if "rights" in item and item["rights"]:
                ET.SubElement(e_entry, "rights").text = item["rights"]
            summary = item["summary"]
            if summary:
                summaryd = {
                    "type" : "text",
                    "text" : item["summary"],
                    "link" : ""}
                ET.SubElement(e_entry, "summary", {
                    "type": summaryd["type"]}).text = summaryd["text"]
            content = item["content"] if "content" in item else None
            if content:
                e_content = ET.SubElement(e_entry, "content", {
                    "type"  : content["type"]})
                # FIXME Invalid XML.
                #       This could be an issue of Docutils
                #       Function "publish_parts", option "fragment".
                #element_xhtml = ET.fromstring(content["text"])
                element_xhtml = ET.HTML(content["text"])

                # TODO Remove elements html, body, and main; and comment nodes.
                #elements = element_xhtml.xpath("//*")
                #elements.reverse()
                #for element in elements: element.getparent().remove(element)

                #if not element_xhtml:
                #    element_xhtml = ET.fromstring(
                #        content["text"], parser=ET.XMLParser(recover=True))

                #c_div = ET.SubElement(e_content, "div", {
                #    "xhtml" : "http://www.w3.org/1999/xhtml"})
                #c_div.append(element_xhtml)

                # Extract element "main"; add attribute "xmlns" and rename tag to "div".
                element_content = element_xhtml.xpath("//main")[0]
                element_content.tag = "div"
                element_content.attrib["xmlns"] = "http://www.w3.org/1999/xhtml"

                # Remove all comment nodes.
                elements_comment = element_xhtml.xpath("//comment()")
                for element_comment in elements_comment:
                    element_comment.getparent().remove(element_comment)

                e_content.append(element_content)

                #element_xhtml = ET.fromstring(
                #    "<div xmlns:xhtml=\"http://www.w3.org/1999/xhtml\">" +
                #    content["text"] +
                #    "</div>", parser=ET.XMLParser(recover=True))
                #e_content.append(element_xhtml)
            categories = item["categories"]
            if categories:
                for category in categories:
                    ET.SubElement(e_entry, "category", {
                        "term": category["term"],
                        "label": category["label"],
                        "scheme": category["scheme"]})

            ET.SubElement(e_entry, "id").text = item["id"]
        xslt_reference = ET.ProcessingInstruction(
            "xml-stylesheet",
            f"type=\"text/xml\" href=\"{filepath_xslt}\"")
        e_feed.addprevious(xslt_reference)
        xml_data = ET.ElementTree(e_feed)
        xml_data_bytes = ET.tostring(
            xml_data,
            pretty_print=True,
            xml_declaration=True,
            encoding="utf-8")
        xml_data_str = xml_data_bytes.decode("utf-8")
        return xml_data_str
