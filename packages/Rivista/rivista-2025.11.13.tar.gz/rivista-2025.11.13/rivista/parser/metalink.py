#!/usr/bin/python
# -*- coding: utf-8 -*-

from rivista.property.publish import publish_properties
from rivista.utility.logger import UtilityLogger
import sys
#import xml.etree.ElementTree as ET
import lxml.etree as ET

logger = UtilityLogger(__name__)

metalink_properties = publish_properties.settings["metalink"]
publisher_name = metalink_properties["publisher"]["name"]
publisher_url = metalink_properties["publisher"]["url"]
copyright = metalink_properties["copyright"]
language = metalink_properties["language"]
logo = metalink_properties["logo"]

class ParserMetalink:

    def meta4(metalink: dict):
        """
        Generate a Metalink document.
        """
        e_metalink = ET.Element("metalink")
        e_metalink.set("xmlns", "urn:ietf:params:xml:ns:metalink")
        e_metalink = ET.Element("metalink", nsmap={
            None   : "urn:ietf:params:xml:ns:metalink",
            "atom" : "http://www.w3.org/2005/Atom"})
        #if len(metalink["files"]) > 1:
        #    e_files = ET.SubElement(e_metalink, "files")
        #    for file in metalink["files"]:
        #        element_file(e_files, file: dict)
        #else:
        #    element_file(e_metalink, metalink["files"][0]: dict)
        if "links" in metalink:
            for link in metalink["links"]:
                ET.SubElement(e_metalink, "{http://www.w3.org/2005/Atom}link", {
                    "href"  : link["href"],
                    "rel"   : link["rel"],
                    "title" : link["title"],
                    "type"  : link["type"]})
        for file in metalink["files"]:
            e_file = ET.SubElement(e_metalink, "file")
            e_file.set("name", file["name"])
            ET.SubElement(e_file, "copyright").text = file["copyright"] or copyright
            ET.SubElement(e_file, "description").text = file["description"]
            if "hashes" in file:
                for hash in file["hashes"]:
                    e_hash = ET.SubElement(e_file, "hash")
                    e_hash.set("type", hash["type"])
                    e_hash.text = hash["hash"]
            ET.SubElement(e_file, "identity").text = file["identity"]
            for language in file["languages"]:
                ET.SubElement(e_file, "language").text = language
            ET.SubElement(e_file, "logo").text = file["logo"] or logo
            if "metaurls" in file:
                for metaurl in file["metaurls"]:
                    e_metaurl = ET.SubElement(e_file, "metaurl")
                    e_metaurl.set("mediatype", metaurl["mediatype"])
                    e_metaurl.set("name", metaurl["location"])
                    e_metaurl.set("priority", metaurl["priority"])
                    e_metaurl.text = metaurl["url"]
            if "os" in file:
                for os in file["os"]:
                    ET.SubElement(e_file, "os").text = os
            if ("pieces" in file and
                "hashes" in file["pieces"] and
                file["pieces"]["hashes"]):
                e_pieces = ET.SubElement(e_file, "pieces")
                e_pieces.set("length", file["pieces"]["length"])
                e_pieces.set("type", file["pieces"]["type"])
                for hash in file["pieces"]["hashes"]:
                    ET.SubElement(e_pieces, "hash").text = hash
            e_publisher = ET.SubElement(e_file, "publisher")
            e_publisher.set("name", publisher_name)
            e_publisher.set("url", publisher_url)
            if "signatures" in file:
                for signature in file["signatures"]:
                    e_signature = ET.SubElement(e_file, "signature")
                    e_signature.set("mediatype", signature["mediatype"])
                    e_signature.text = signature["key"]
            ET.SubElement(e_file, "size").text = file["size"]
            for url in file["urls"]:
                e_url = ET.SubElement(e_file, "url")
                e_url.set("location", url["location"])
                e_url.set("priority", url["priority"])
                e_url.text = url["url"]
            ET.SubElement(e_file, "version").text = file["version"]
        ET.SubElement(e_metalink, "generator").text = "Rivista Voyager"
        e_origin = ET.SubElement(e_metalink, "origin")
        e_origin.set("dynamic", metalink["dynamic"])
        e_origin.text = metalink["origin"]
        ET.SubElement(e_metalink, "published").text = metalink["published"]
        ET.SubElement(e_metalink, "updated").text = metalink["updated"]
        xslt_reference = ET.ProcessingInstruction(
            "xml-stylesheet",
            "type=\"text/xml\" href=\"/xslt/page-metalink.xslt\"")
        e_metalink.addprevious(xslt_reference)
        xml_data = ET.ElementTree(e_metalink)
        xml_data_bytes = ET.tostring(xml_data, pretty_print=True,
                                     xml_declaration=True, encoding="utf-8")
        xml_data_str = xml_data_bytes.decode("utf-8")
        return xml_data_str

    def element_file(e_element, file: dict) -> None:
        """Generate a Metalink 3 element file."""
        e_file = ET.SubElement(e_element, "file")
        e_file.set("name", file["name"])
        ET.SubElement(e_file, "copyright").text = file["copyright"] or copyright
        ET.SubElement(e_file, "description").text = file["description"]
        e_hash = ET.SubElement(e_file, "hash").text = file["hash"]
        e_hash.set("type", file["hashtype"])
        ET.SubElement(e_file, "identity").text = file["identity"]
        ET.SubElement(e_file, "language").text = file["language"] or language
        ET.SubElement(e_file, "logo").text = file["logo"] or logo
        for metaurl in file["metaurls"]:
            e_metaurl = ET.SubElement(e_file, "metaurl")
            e_metaurl.text = metaurl["iri"]
            e_metaurl.set("mediatype", url["mediatype"])
            e_metaurl.set("name", url["location"])
            e_metaurl.set("priority", url["priority"])
        if file["os"]: ET.SubElement(e_file, "os").text = file["os"]
        if file["pieces"]["hashes"]:
            e_pieces = ET.SubElement(e_file, "pieces")
            e_pieces.set("length", file["pieces"]["length"])
            e_pieces.set("type", file["pieces"]["type"])
            for hash in file["pieces"]["hashes"]:
                ET.SubElement(e_pieces, "hash")
        e_publisher = ET.SubElement(e_file, "publisher")
        e_publisher.set("name", publisher_name)
        e_publisher.set("url", publisher_url)
        e_signature = ET.SubElement(e_file, "signature")
        e_signature.set("mediatype", file["signature"]["mediatype"])
        e_signature.text = file["signature"]["key"]
        ET.SubElement(e_file, "size").text = file["size"]
        for url in file["urls"]:
            e_url = ET.SubElement(e_file, "url")
            e_url.text = url["iri"]
            e_url.set("location", url["location"])
            e_url.set("priority", url["priority"])
        ET.SubElement(e_file, "version").text = file["version"]
