#!/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio
import lxml.etree as ET
import os
from rivista.property.publish import publish_properties
from rivista.utility.html import UtilityHtml

class UtilitySearch:

    async def query(query: str, parameters=None) -> dict:
        query_lower = query.lower()
        directory_output_posts = os.path.join(publish_properties.directory_output, "posts")
        atom = {}
        atom["title"] = "Search"
        atom["subtitle"] = f"Results for query “{query}”"
        atom["lang"] = publish_properties.locale
        atom["rights"] = publish_properties.rights
        atom["links"] = []
        for link in publish_properties.settings_map["atom"]["link"]:
            atom["links"].append(
                {"href"  : link["href"],
                #"hreflang" : link["hreflang"],
                "rel"   : link["rel"],
                "title" : link["title"] if "title" in link else "",
                "type"  : link["type"]})
        atom["items"] = []
        xmlns = "{http://www.w3.org/2005/Atom}"
        parameters_xmlns = []
        if not parameters: parameters=["content", "summary", "title"]
        for parameter in parameters:
            parameters_xmlns.append(f"{xmlns}{parameter}")
        for directory in os.listdir(directory_output_posts):
            await asyncio.sleep(0)
            pathname = os.path.join(directory_output_posts, directory)
            if os.path.isdir(pathname):
                filepath = os.path.join(pathname, "index.atom")
                if os.path.exists(filepath):
                    try:
                        # Parse XML
                        tree = ET.parse(filepath)
                        #root = tree.getroot()
                        root = tree.find(f"{xmlns}entry")
                        # Search for elements of query
                        for element in root.iter():
                            #await asyncio.sleep(0)
                            if element.tag in parameters_xmlns:
                                if element.text:
                                    plaintext = UtilityHtml.remove_html_tags(element.text)
                                    if plaintext and query_lower in plaintext.lower():
                                        ix = plaintext.lower().index(query_lower)
                                        if ix < 50:
                                            excerpt = plaintext[:500]
                                        else:
                                            excerpt = plaintext[ix-50:][:500]
                                        filepath_list = filepath.split("/")
                                        part_path = f"/{filepath_list[7]}/{filepath_list[8]}"
                                        atom_item = {}
                                        tag = element.tag.replace(xmlns, "")
                                        #title = tree.find(f"{xmlns}title").text
                                        #atom_item["title"] = f"{title} ({tag})"
                                        atom_item["title"] = tree.find(f"{xmlns}title").text
                                        atom_item["links"] = [
                                            {"href" : part_path,
                                            "rel"  : "self",
                                            "title" : part_path,
                                            "type"  : "application/atom+xml"}]
                                        atom_item["summary"] = f"[{tag.capitalize()}] {excerpt.strip()}"
                                        atom_item["published"] = root.find(f"{xmlns}published").text
                                        atom_item["updated"] = root.find(f"{xmlns}updated").text
                                        atom_item["categories"] = []
                                        atom_item["id"] = ""
                                        atom["items"].append(atom_item)
                    except ET.ParseError as e:
                        print(f"Error parsing {filepath}: {e}")
        if not atom["items"]: atom["items"] = [{
            "title" : "No results",
            "summary" : f"No results were found for query “{query}”",
            "published" : "",
            "updated" : "",
            "id" : "",
            "categories": []
        }]
        return atom
