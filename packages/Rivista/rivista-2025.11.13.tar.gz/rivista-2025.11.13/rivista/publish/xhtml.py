#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from rivista.interface.xmpp.client import InterfaceXmppClient
from rivista.interface.xmpp.ping import InterfaceXmppPing
from rivista.interface.xmpp.pubsub import InsterfaceXmppPubsub
from rivista.parser.atom import ParserAtom
from rivista.parser.metalink import ParserMetalink
from rivista.parser.toml import ParserToml
from rivista.parser.xml import ParserXml
from rivista.parser.xslt import ParserXslt
from rivista.property.publish import publish_properties
from rivista.utility.config import Data
from rivista.utility.csv import UtilityCsv
from rivista.utility.document import UtilityDocument
from rivista.utility.html import UtilityHtml
from rivista.utility.logger import UtilityLogger
from rivista.utility.rst import UtilityRst
from rivista.utility.text import UtilityText
from rivista.utility.uri import UtilityUri
from slixmpp.stanza.iq import Iq
import sys

logger = UtilityLogger(__name__)

class PublishXml:

    def initiate() -> None:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        directory_source = publish_properties.directory_source
        # Generate root files
        for filename in os.listdir(directory_source):
            pathname = os.path.join(directory_source, filename)
            if os.path.isfile(pathname):
                directory = filename[:-4]
                directory_output_directory = os.path.join(
                    publish_properties.directory_output, directory)
                if not os.path.exists(directory_output_directory):
                    os.mkdir(directory_output_directory)
                if filename == "index.rst":
                    PublishXml.page(pathname, filename=filename)
                else:
                    PublishXml.page(pathname, directory=directory)
        # Generate subsequent files
        for root, directories, filenames in os.walk(directory_source):
            for directory in directories:
                pathname = os.path.join(root, directory)
                directory_output_directory = os.path.join(
                    publish_properties.directory_output, directory)
                if not os.path.exists(directory_output_directory):
                    os.mkdir(directory_output_directory)
                index_file = os.path.join(pathname, "index.rst")
                # TODO Do not accept index files when there are no more other files.
                if os.path.exists(index_file):
                    PublishXml.pages(pathname, directory, index_file)
                for filename_ in os.listdir(pathname):
                    if filename_ == "index.rst": continue
                    pathname_ = os.path.join(pathname, filename_)
                    directory_output_directory_filename_ = os.path.join(
                        publish_properties.directory_output, directory, filename_[:-4])
                    if not os.path.exists(directory_output_directory_filename_):
                        os.mkdir(directory_output_directory_filename_)
                    if os.path.isfile(pathname_):
                        PublishXml.page(pathname_, filename=filename_,
                                        directory=directory)
                    elif os.path.isdir(pathname_):
                        print("Warning.")
        #directory_source_posts = publish_properties.directory_source_posts
        #for filename in os.listdir(directory_source_posts):
        #    PublishXml.page(directory_source_posts, filename=filename, directory="posts")
        #PublishXml.pages(directory_source_posts, "posts")

    def page(pathname, filename="", directory="") -> None:
        """Create an Atom Syndication Format with a single entry"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{filename}	Start")
        logger.debug(f"{function_name}	{pathname}	Start")
        logger.debug(f"{function_name}	{directory}	Start")
        filename_xslt = "/xslt/page-article.xslt"
        rst_content_str = open(pathname, mode="r").read()
        xhtml_content_str = UtilityDocument.convert(rst_content_str, "xhtml")
        properties = UtilityRst.properties(rst_content_str)
        # Generate Atom
        atom = {}
        atom["icon"] = "/icon.svg" if os.path.exists(publish_properties.filename_icon) else ""
        atom["logo"] = "/logo.svg" if os.path.exists(publish_properties.filename_logo) else ""
        atom["lang"] = properties["lang"] or publish_properties.locale
        atom["rights"] = properties["rights"] or publish_properties.rights
        atom["title"] = properties["title"]
        atom["subtitle"] = properties["summary"]
        atom["categories"] = []
        for tag in properties["category"].replace("\n","").split(","):
            label = tag.strip()
            term = tag.lower().strip().replace(" ", "-")
            atom["categories"].append({
                "term"   : term,
                "label"  : label,
                "scheme" : "/tag"})
            # TODO Add "term" and "label".
        atom["links"] = []
        properties_links = UtilityCsv.parse_csv_to_dict(properties["links"])
        for properties_link in properties_links:
            if ("rel" in properties_link and
                properties_link["rel"] in ("enclosure", "related")):
                continue
            if "href" in properties_link:
                if (properties_link["title"] == "html" and
                    ".xsl" in properties_link["href"] and
                    properties_link["rel"] == "stylesheet" and
                    properties_link["type"] == "application/xslt+xml"):
                    filename_xslt = properties_link["href"]
                address = properties_link["href"]
                if (not address.startswith("/") and
                    not UtilityUri.has_scheme(address)):
                    # Assuming relations previous and next
                    address = f"/{directory}/{address}"
                if properties_link["rel"] == "microsummary": continue
                atom["links"].append({
                    "href"   : address,
                    "length" : properties_link["length"] if "length" in properties_link and properties_link["length"] else "",
                    "rel"    : properties_link["rel"] if "rel" in properties_link and properties_link["rel"] else "",
                    "title"  : properties_link["title"] if "title" in properties_link and properties_link["title"] else "",
                    "type"   : properties_link["type"] if "type" in properties_link and properties_link["type"] else ""})
        identifier = filename[:-4] if filename and filename != "index.rst" else ""
        atom["links"].append({
            "href"  : f"/{directory}/{identifier}/" if directory or identifier else "/",
            "rel"   : "self",
            "title" : "",
            "type"  : ""})
        atom["links"].append({
            "href"  : f"/{directory}/{identifier}/index.atom" if directory or identifier else "/index.atom",
            "rel"   : "alternate",
            "title" : "",
            "type"  : "application/atom+xml"})
        atom["links"].append({
            "href"  : f"/{directory}/{identifier}/index.html" if directory or identifier else "/index.html",
            "rel"   : "alternate",
            "title" : "",
            "type"  : "application/xhtml+xml"})
        for link in publish_properties.settings_map["atom"]["link"]:
            atom["links"].append({
                "href"  : link["href"],
                #"hreflang" : link["hreflang"],
                "rel"   : link["rel"],
                "title" : link["title"] if "title" in link else "",
                "type"  : link["type"]})
        atom_item = {}
        atom_item["title"] = properties["title"]
        atom_item["rights"] = properties["rights"]
        hostname_gemini = publish_properties.settings["domain-name"]["gemini"]
        jid_bare = publish_properties.pubsub
        node_name = publish_properties.node
        properties_link = properties["link"]
        atom_item["links"] = [
            {"href"  : f"/{directory}/{properties_link}/",
             "rel"   : "self",
             "title" : properties["title"],
             "type"  : ""},
            {"href"  : f"xmpp:{jid_bare}?;node={node_name};item={properties_link}",
             "rel"   : "alternate",
             "title" : properties["title"],
             "type"  : ""}, # application/atom+xml
            {"href"  : f"/{directory}/{properties_link}/index.atom",
             "rel"   : "alternate",
             "title" : properties["title"],
             "type"  : "application/atom+xml"},
            {"href"  : f"/{directory}/{properties_link}/index.html",
             "rel"   : "alternate",
             "title" : properties["title"],
             "type"  : "application/xhtml+xml"},
            {"href"  : f"{hostname_gemini}/{directory}/{properties_link}",
             "rel"   : "alternate",
             "title" : properties["title"],
             "type"  : "text/gemini"},
            {"href"   : f"/{directory}/{properties_link}/enclosures.meta4",
             "length" : "",
             "rel"    : "enclosure",
             "title"  : "Download this article",
             "type"   : "application/metalink4-xml"},
            {"href"   : f"/{directory}/{properties_link}/source.rst",
             "length" : "",
             "rel"    : "enclosure",
             "title"  : "Article source",
             "type"   : "text/x-rst"},
            {"href"  : f"/{directory}/{properties_link}/edit.atom",
             "rel"   : "edit",
             "title" : "",
             "type"  : "application/atom+xml"},
            {"href"  : f"/{directory}/{properties_link}/edit.html",
             "rel"   : "edit",
             "title" : "",
             "type"  : "application/xhtml+xml"}]
        properties_links = UtilityCsv.parse_csv_to_dict(properties["links"])
        for properties_link in properties_links:
            if ("rel" in properties_link and
                properties_link["rel"] in ("next", "previous")):
                continue
            if "href" in properties_link:
                address = properties_link["href"]
                if (not address.startswith("/") and
                    not UtilityUri.has_scheme(address)):
                    if properties_link["rel"] in ("enclosure", "microsummary"):
                        address = f"/{directory}/{identifier}/{address}"
                    else:
                        address = f"/{directory}/{address}"
                if properties_link["rel"] == "microsummary":
                    address = address + ".ms.txt"
                atom_item["links"].append({
                    "href"   : address,
                    "length" : properties_link["length"] if "length" in properties_link and properties_link["length"] else "",
                    "rel"    : properties_link["rel"] if "rel" in properties_link and properties_link["rel"] else "",
                    "title"  : properties_link["title"] if "title" in properties_link and properties_link["title"] else "",
                    "type"   : properties_link["type"] if "type" in properties_link and properties_link["type"] else ""})
        filename_atom = f"{identifier}.atom" if filename else "index.atom"
        atom_item["summary"] = properties["summary"]
        atom_item["content"] = {
            "text" : xhtml_content_str,
            "type" : "text/html"}
        atom_item["published"] = properties["published"] if "published" in properties else ""
        atom_item["updated"] = properties["updated"]
        for people in ("author", "contributor"):
            properties_peoples = UtilityCsv.parse_csv_to_dict(properties[people])
            atom_item[people] = []
            for properties_people in properties_peoples:
                if "name" in properties_people:
                    # TODO Create an absolute HTTP URL.
                    atom_item[people].append({
                        "name" : properties_people["name"],
                        "uri"  : properties_people["uri"] if "uri" in properties_people else ""})
        atom_item["categories"] = atom["categories"]
        atom_item["id"] = properties["id"]
        atom["items"] = [atom_item]
        atom_as_string = ParserAtom.document(atom, filename_xslt)
        directory_output = publish_properties.directory_output
        filepath_atom = os.path.join(
            directory_output, directory, identifier, "index.atom")
        with open(filepath_atom, "w") as fn: fn.write(atom_as_string)
        filepath_source = os.path.join(
            directory_output, directory, identifier, "source.rst")
        try:
            os.symlink(pathname, filepath_source)
        except FileExistsError:
            logger.info(f"Symlink already exists: {directory_output}")
        except PermissionError:
            logger.error(f"Permission denied for the creation of link: {directory_output}")
        except OSError as e:
            logger.error(f"OSError: {str(e)}")
        # Generate HTML of Atom
        filepath_xslt_atom = os.path.join(
            publish_properties.directory_xslt, filename_xslt)
        atom_as_element_tree = ParserXml.create_element_tree_from_file(
            filepath_atom)
        atom_html_as_str = ParserXslt.transform_data(
            atom_as_element_tree, filepath_xslt_atom)
        filepath_atom_html = os.path.join(
            directory_output, directory, identifier, "index.html")
        with open(filepath_atom_html, "w") as fn: fn.write(atom_html_as_str)

    def pages(pathname, directory, index_file="") -> None:
        """Create an Atom Syndication Format with a multiple entries"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{directory}	Start")
        logger.debug(f"{function_name}	{pathname}	Start")
        filename_xslt = "/xslt/page-selection.xslt"
        if index_file:
            rst_content_str = open(index_file, mode="r").read()
            xhtml_content_str = UtilityDocument.convert(rst_content_str, "xhtml")
            properties = UtilityRst.properties(rst_content_str)
        else:
            properties = {
                "title" : directory.capitalize(),
                "subtitle" : f"Recent updates for {directory}"
            }
        # Generate Atom
        atom = {}
        atom["icon"] = "/icon.svg" if os.path.exists(publish_properties.filename_icon) else ""
        atom["logo"] = "/logo.svg" if os.path.exists(publish_properties.filename_logo) else ""
        atom["lang"] = properties["lang"] or publish_properties.locale
        atom["rights"] = properties["rights"] or publish_properties.rights
        atom["title"] = properties["title"]
        atom["subtitle"] = properties["subtitle"] or properties["summary"]
        atom["categories"] = []
        for tag in properties["category"].replace("\n","").split(","):
            label = tag.strip()
            term = tag.lower().strip().replace(" ", "-")
            atom["categories"].append({
                "term"   : term,
                "label"  : label,
                "scheme" : "/tag"})
        if index_file:
            if properties["summary"]:
                atom["summary"] = {
                    "text" : properties["summary"],
                    "type" : "text/plain"}
            else:
                atom["summary"] = {
                    "text" : xhtml_content_str,
                    "type" : "text/html"}
        else:
            atom["summary"] =  ""
        atom["links"] = []
        properties_links = UtilityCsv.parse_csv_to_dict(properties["links"])
        for properties_link in properties_links:
            if "href" in properties_link:
                if ("rel" in properties_link and
                    properties_link["rel"] in ("enclosure", "related")):
                    continue
                if (properties_link["title"] == "html" and
                    ".xsl" in properties_link["href"] and
                    properties_link["rel"] == "stylesheet" and
                    properties_link["type"] == "application/xslt+xml"):
                    filename_xslt = properties_link["href"]
                address = properties_link["href"]
                if (not address.startswith("/") and
                    not UtilityUri.has_scheme(address)):
                    # Assuming relations previous and next
                    address = f"/{directory}/{address}"
                atom["links"].append({
                    "href"   : address,
                    "length" : properties_link["length"] if "length" in properties_link and properties_link["length"] else "",
                    "rel"    : properties_link["rel"] if "rel" in properties_link and properties_link["rel"] else "",
                    "title"  : properties_link["title"] if "title" in properties_link and properties_link["title"] else "",
                    "type"   : properties_link["type"] if "type" in properties_link and properties_link["type"] else ""})
        atom["links"].append({
            "href" : f"/{directory}/",
            "rel"  : "self",
            "title" : "",
            "type"  : ""})
        atom["links"].append({
            "href" : f"/{directory}/index.atom",
            "rel"  : "alternate",
            "title" : "",
            "type"  : "application/atom+xml"})
        atom["links"].append({
            "href" : f"/{directory}/index.html",
            "rel"  : "alternate",
            "title" : "",
            "type"  : "application/xhtml+xml"})
        for link in publish_properties.settings_map["atom"]["link"]:
            atom["links"].append({
                "href"   : link["href"],
                #"hreflang" : link["hreflang"],
                "rel"   : link["rel"],
                "title" : link["title"] if "title" in link else "",
                "type"  : link["type"]})
        atom["items"] = []
        filenames = os.listdir(pathname)
        if filenames: filenames.sort(reverse=True)
        for filename in filenames:
            if filename == "index.rst": continue
            rst_file = os.path.join(pathname, filename)
            rst_data = open(rst_file, mode="r")
            rst_content_str = rst_data.read()
            xhtml_content_str = UtilityDocument.convert(rst_content_str,
                                                        "xhtml")
            properties = UtilityRst.properties(rst_content_str)
            atom_item = {}
            atom_item["title"] = properties["title"]
            atom_item["rights"] = properties["rights"]
            properties_link = properties["link"]
            hostname_gemini = publish_properties.settings["domain-name"]["gemini"]
            hostname_http = publish_properties.settings["domain-name"]["http"]
            jid_bare = publish_properties.pubsub
            node_name = publish_properties.node
            atom_item["links"] = [
                {"href" : f"/{directory}/{properties_link}/", # filename[:-4]
                 "rel"  : "self",
                 "title" : properties["title"],
                 "type"  : ""},
                {"href"  : f"xmpp:{jid_bare}?;node={node_name};item={properties_link}",
                 "rel"   : "alternate",
                 "title" : properties["title"],
                 "type"  : ""}, # application/atom+xml
                {"href"  : f"/{directory}/{properties_link}/index.atom",
                 "rel"   : "alternate",
                 "title" : properties["title"],
                 "type"  : "application/atom+xml"},
                {"href"  : f"/{directory}/{properties_link}/index.html",
                 "rel"   : "alternate",
                 "title" : properties["title"],
                 "type"  : "application/xhtml+xml"},
                {"href"  : f"{hostname_gemini}/{directory}/{properties_link}",
                 "rel"   : "alternate",
                 "title" : properties["title"],
                 "type"  : "text/gemini"}]
            identifier = filename[:-4] if filename and filename != "index.rst" else ""
            properties_links = UtilityCsv.parse_csv_to_dict(properties["links"])
            for properties_link in properties_links:
                if ("rel" in properties_link and
                    properties_link["rel"] in ("next", "previous")):
                    continue
                if "href" in properties_link:
                    address = properties_link["href"]
                    if (not address.startswith("/") and
                        not UtilityUri.has_scheme(address)):
                        if properties_link["rel"] in ("enclosure", "microsummary"):
                            address = f"/{directory}/{identifier}/{address}"
                        else:
                            address = f"/{directory}/{address}"
                    if properties_link["rel"] == "microsummary":
                        address = address + ".ms.txt"
                    atom_item["links"].append({
                        "href"   : address,
                        "length" : properties_link["length"] if "length" in properties_link and properties_link["length"] else "",
                        "rel"    : properties_link["rel"] if "rel" in properties_link and properties_link["rel"] else "",
                        "title"  : properties_link["title"] if "title" in properties_link and properties_link["title"] else "",
                        "type"   : properties_link["type"] if "type" in properties_link and properties_link["type"] else ""})
            atom_item["summary"] = properties["summary"]
            atom_item["content"] = {
                "text" : xhtml_content_str,
                "type" : "text/html"}
            atom_item["rights"] = properties["rights"] or publish_properties.rights
            atom_item["published"] = properties["published"] if "published" in properties else ""
            atom_item["updated"] = properties["updated"]
            for people in ("author", "contributor"):
                properties_peoples = UtilityCsv.parse_csv_to_dict(properties[people])
                atom_item[people] = []
                for properties_people in properties_peoples:
                    if "name" in properties_people:
                        # TODO Create an absolute HTTP URL.
                        atom_item[people].append({
                            "name" : properties_people["name"],
                            "uri"  : properties_people["uri"] if "uri" in properties_people else ""})
            atom_item["categories"] = atom["categories"]
            atom_item["id"] = properties["id"]
            atom["items"].append(atom_item)
        atom_as_string = ParserAtom.document(atom, filename_xslt)
        directory_output = publish_properties.directory_output
        filepath_atom = os.path.join(directory_output, directory, "index.atom")
        with open(filepath_atom, "w") as fn: fn.write(atom_as_string)
        # Generate HTML of Atom
        filepath_xslt = os.path.join(
            publish_properties.directory_xslt, f"{filename_xslt}")
        atom_as_element_tree = ParserXml.create_element_tree_from_file(
            filepath_atom)
        atom_html_as_str = ParserXslt.transform_data(atom_as_element_tree, filepath_xslt)
        filepath_atom_html = os.path.join(
            directory_output, directory, "index.html")
        with open(filepath_atom_html, "w") as fn: fn.write(atom_html_as_str)

    # NOTE Utilize slixmpp for data and vCard, and prioritize content of rST.
    #def profile(directory, filename) -> None:

    # TODO Save data to cookies so it can be restored in case of request to complete form; or
    #      Save data to ~Atom~ TOML file for given IP address or cookie.
    #def contact() -> None:

    # NOTE Consider page "about" instead of mixing with page "contact".
    def contact() -> None:
        """Create an Atom Syndication Format with a single entry"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        filename_xslt = "/xslt/page-article.xslt"
        directory_data = Data.get_directory()
        directory_xmpp = os.path.join(directory_data, "xmpp")
        vcard_filename = os.path.join(directory_xmpp, "vcard.toml")
        directory_output = publish_properties.directory_output
        directory_output_contact = os.path.join(directory_output, "contact")
        if (os.path.exists(directory_output_contact) and
            os.path.exists(vcard_filename)):
            vcard = ParserToml.open_file(vcard_filename)
            rst_file = os.path.join(publish_properties.directory_source, "contact.rst")
            rst_data = open(rst_file, mode="r")
            rst_content_str = rst_data.read()
            #xhtml_content_str = UtilityDocument.convert(rst_content_str,
            #                                            "xhtml")
            properties = UtilityRst.properties(rst_content_str)
            # Generate Atom
            atom = {}
            atom["icon"] = "/icon.svg" if os.path.exists(publish_properties.filename_icon) else ""
            atom["logo"] = "/logo.svg" if os.path.exists(publish_properties.filename_logo) else ""
            atom["lang"] = publish_properties.locale
            atom["rights"] = publish_properties.rights
            atom["title"] = vcard["name"]
            atom["subtitle"] = vcard["role"]
            atom["categories"] = []
            atom["links"] = []
            properties_links = UtilityCsv.parse_csv_to_dict(properties["links"])
            for properties_link in properties_links:
                if "href" in properties_link:
                    if (properties_link["title"] == "html" and
                        ".xsl" in properties_link["href"] and
                        properties_link["rel"] == "stylesheet" and
                        properties_link["type"] == "application/xslt+xml"):
                        filename_xslt = properties_link["href"]
                    address = properties_link["href"]
                    if (not address.startswith("/") and
                        not UtilityUri.has_scheme(address)):
                        address = f"/{directory}/{address}" # /index.atom
                    if properties_link["rel"] == "microsummary": continue
                    atom["links"].append({
                        "href"   : address,
                        "length" : properties_link["length"] if "length" in properties_link and properties_link["length"] else "",
                        "rel"    : properties_link["rel"] if "rel" in properties_link and properties_link["rel"] else "",
                        "title"  : properties_link["title"] if "title" in properties_link and properties_link["title"] else "",
                        "type"   : properties_link["type"] if "type" in properties_link and properties_link["type"] else ""})
            atom["links"].append({
                "href" : "/contact/",
                "rel"  : "self",
                "title" : "",
                "type"  : ""})
            atom["links"].append({
                "href" : "/contact/index.atom",
                "rel"  : "alternate",
                "title" : "",
                "type"  : "application/atom+xml"})
            atom["links"].append({
                "href" : "/contact/index.html",
                "rel"  : "alternate",
                "title" : "",
                "type"  : "application/xhtml+xml"})
            for link in publish_properties.settings_map["atom"]["link"]:
                atom["links"].append({
                    "href" : link["href"],
                    #"hreflang" : link["hreflang"],
                    "rel"   : link["rel"],
                    "title" : link["title"] if "title" in link else "",
                    "type"  : link["type"]})
            atom_item = {}
            atom_item["title"] = vcard["name"]
            # TODO Analyze content type.
            atom_item["links"] = [
                {"href"  : vcard["url"],
                 "rel"   : "alternate",
                 "title" : "URI",
                 "type"  : "application/octet-stream"},
                {"href"   : "/profile/image",
                 "length" : "",
                 "rel"    : "enclosure",
                 "title"  : "Photograph",
                 "type"   : "application/octet-stream"},
                {"href"   : "/profile/qr.png",
                 "length" : "",
                 "rel"    : "enclosure",
                 "title"  : "QR Code",
                 "type"   : "image/png"}]
            # TODO Iterate links
            # Skip navigational directives
            #if properties_link["rel"] in ("next", "previous"):
            #      continue
            # Add Microsummary
            #if properties_link["rel"] == "microsummary":
            #    address = address + ".ms.txt"
            atom_item["summary"] = vcard["role"]
            atom_item["content"] = {
                "text" : vcard["note"],
                "type" : "text/plain"}
            atom_item["published"] = ""
            atom_item["updated"] = ""
            atom_item["author"] = []
            atom_item["contributor"] = []
            atom_item["categories"] = [
                {"term"   : "contact",
                 "label"  : "Contact",
                 "scheme" : "/tag"},
                {"term"   : "xmpp",
                 "label"  : "XMPP",
                 "scheme" : "/tag"}]
            atom_item["id"] = ""
            atom["items"] = [atom_item]
            filepath_atom = os.path.join(directory_output, "contact", "index.atom")
            atom_as_string = ParserAtom.document(atom, filename_xslt)
            with open(filepath_atom, "w") as fn: fn.write(atom_as_string)
            directory_xslt = publish_properties.directory_xslt
            filepath_xslt = os.path.join(directory_xslt, filename_xslt)
            # Generate HTML of Atom
            atom_as_element_tree = ParserXml.create_element_tree_from_file(
                filepath_atom)
            atom_html_as_str = ParserXslt.transform_data(atom_as_element_tree, filepath_xslt)
            filepath_atom_html = os.path.join(
                directory_output, "contact", "index.html")
            with open(filepath_atom_html, "w") as fn: fn.write(atom_html_as_str)

    def edit(pathname, identifier, directory="") -> None:
        """Create an Atom Syndication Format for editing"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{identifier}	Start")
        logger.debug(f"{function_name}	{pathname}	Start")
        logger.debug(f"{function_name}	{directory}	Start")
        rst_content_str = open(pathname, mode="r").read()
        # Generate Atom
        properties = UtilityRst.properties(rst_content_str)
        atom = {}
        atom["icon"] = "/icon.svg" if os.path.exists(publish_properties.filename_icon) else ""
        atom["logo"] = "/logo.svg" if os.path.exists(publish_properties.filename_logo) else ""
        atom["title"] = properties["title"]
        atom["subtitle"] = properties["summary"]
        atom["lang"] = properties["lang"] or publish_properties.locale
        atom["rights"] = properties["rights"] or publish_properties.rights
        atom["links"] = []
        atom["links"].append({
            "href" : f"/{directory}/{identifier}/",
            "rel"  : "self",
            "title" : "",
            "type"  : ""})
        atom["links"].append({
            "href" : f"/{directory}/{identifier}/edit.atom",
            "rel"  : "self",
            "title" : "",
            "type"  : "application/atom+xml"})
        atom["links"].append({
            "href" : f"/{directory}/{identifier}/edit.html",
            "rel"  : "self",
            "title" : "",
            "type"  : "application/xhtml+xml"})
        atom["categories"] = []
        for tag in properties["category"].replace("\n","").split(","):
            label = tag.strip()
            term = tag.lower().strip().replace(" ", "-")
            atom["categories"].append({
                "term"   : term,
                "label"  : label,
                "scheme" : "/tag"})
        atom_item = {}
        atom_item["title"] = properties["title"]
        # TODO Add Gemini
        properties_link = properties["link"]
        atom_item["links"] = [
            {"href"  : f"/{directory}/{properties_link}/",
             "rel"   : "self",
             "title" : properties["title"],
             "type"  : ""},
            {"href"  : f"/{directory}/{properties_link}/index.atom",
             "rel"   : "self",
             "title" : properties["title"],
             "type"  : "application/atom+xml"},
            {"href"  : f"/{directory}/{properties_link}/index.html",
             "rel"   : "alternate",
             "title" : properties["title"],
             "type"  : "application/xhtml+xml"}]
        properties_links = UtilityCsv.parse_csv_to_dict(properties["links"])
        for properties_link in properties_links:
            if "href" in properties_link:
                address = properties_link["href"]
                if (not address.startswith("/") and
                    not UtilityUri.has_scheme(address)):
                    address = f"/{directory}/{address}"
                atom_item["links"].append({
                    "href"   : address,
                    "length" : properties_link["length"] if "length" in properties_link and properties_link["length"] else "",
                    "rel"    : properties_link["rel"] if "rel" in properties_link and properties_link["rel"] else "",
                    "title"  : properties_link["title"] if "title" in properties_link and properties_link["title"] else "",
                    "type"   : properties_link["type"] if "type" in properties_link and properties_link["type"] else ""})
        atom_item["summary"] = properties["summary"]
        atom_item["content"] = {
            "text" : rst_content_str,
            "type" : "text/plain"}
        atom_item["published"] = properties["published"] if "published" in properties else ""
        atom_item["updated"] = properties["updated"]
        for people in ("author", "contributor"):
            properties_peoples = UtilityCsv.parse_csv_to_dict(properties[people])
            atom_item[people] = []
            for properties_people in properties_peoples:
                if "name" in properties_people:
                    # TODO Create an absolute HTTP URL.
                    atom_item[people].append({
                        "name" : properties_people["name"],
                        "uri"  : properties_people["uri"] if "uri" in properties_people else ""})
        atom_item["categories"] = atom["categories"]
        atom_item["id"] = properties["id"]
        atom["items"] = [atom_item]
        #identifier = filename[:-4] if filename and filename != "index.rst" else ""
        directory_output = publish_properties.directory_output
        filepath_atom = os.path.join(
            directory_output, directory, identifier, "edit.atom")
        atom_as_string = ParserAtom.document(atom, "/xslt/page-edit.xslt")
        with open(filepath_atom, "w") as fn: fn.write(atom_as_string)
        directory_xslt = publish_properties.directory_xslt
        filepath_xslt = os.path.join(directory_xslt, "page-edit.xslt")
        # Generate HTML of Atom
        atom_as_element_tree = ParserXml.create_element_tree_from_file(
            filepath_atom)
        atom_html_as_str = ParserXslt.transform_data(
            atom_as_element_tree, filepath_xslt)
        filepath_atom_html = os.path.join(
            directory_output, directory, identifier, "edit.html")
        with open(filepath_atom_html, "w") as fn:
            fn.write(atom_html_as_str)

    async def comments_xmpp() -> None:
        """Create an Atom Syndication Format for comments"""
        function_name = sys._getframe().f_code.co_name
        #logger.debug(f"{function_name}	{identifier}	Start")
        #if xmpp:
        address = publish_properties.address
        password = publish_properties.password
        xmpp_instance = InterfaceXmppClient(address, password)
        rtt = await InterfaceXmppPing.to_self(xmpp_instance)
        if xmpp_instance.is_connected or rtt:
            jid = xmpp_instance.boundjid
            jid_bare = publish_properties.pubsub
            comments_pubsub = publish_properties.comments
            node_name = publish_properties.node
            directory = "posts"
            directory_source = publish_properties.directory_source
            directory_source_posts = os.path.join(directory_source, directory)
            for filename in os.listdir(directory_source_posts):
                if filename == "index.rst": continue
                filepath = os.path.join(directory_source_posts, filename)
                rst_content_str = open(filepath, mode="r").read()
                properties = UtilityRst.properties(rst_content_str)
                if properties["comments"] == "locked": continue
                identifier = item_id = filename[:-4]
                comments_node = f"{jid_bare}/{node_name}/{item_id}"
                iq = await InsterfaceXmppPubsub.get_node_items(
                    xmpp_instance, comments_pubsub, comments_node)
                # Generate Atom
                if isinstance(iq, Iq):
                    atom = ParserAtom.extract_atom(iq)
                    atom["links"] = []
                    for link in publish_properties.settings["atom"]["link"]:
                        atom["links"].append({
                            "href"   : link["href"],
                            #"hreflang" : link["hreflang"],
                            "rel"   : link["rel"],
                            "title" : link["title"] if "title" in link else "",
                            "type"  : link["type"]})
                    atom_as_string = ParserAtom.document(atom, "page-comments.xslt")
                    directory_output = publish_properties.directory_output
                    filepath_atom = os.path.join(
                        directory_output, directory, identifier, "comments.atom")
                    with open(filepath_atom, "w") as fn: fn.write(atom_as_string)
                    # Generate HTML of Atom
                    directory_xslt = publish_properties.directory_xslt
                    filepath_xslt = os.path.join(directory_xslt, "page-comments.xslt")
                    atom_as_element_tree = ParserXml.create_element_tree_from_file(
                        filepath_atom)
                    atom_html_as_str = ParserXslt.transform_data(
                        atom_as_element_tree, filepath_xslt)
                    filepath_atom_html = os.path.join(
                        directory_output, directory, identifier, "comments.html")
                    with open(filepath_atom_html, "w") as fn:
                        fn.write(atom_html_as_str)
