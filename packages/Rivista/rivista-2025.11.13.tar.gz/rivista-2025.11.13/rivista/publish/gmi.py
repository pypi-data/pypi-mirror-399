#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from rivista.parser.toml import ParserToml
from rivista.property.publish import publish_properties
from rivista.utility.config import Data
from rivista.utility.csv import UtilityCsv
from rivista.utility.document import UtilityDocument
from rivista.utility.html import UtilityHtml
from rivista.utility.logger import UtilityLogger
from rivista.utility.rst import UtilityRst
from rivista.utility.text import UtilityText
from rivista.utility.uri import UtilityUri
import sys

logger = UtilityLogger(__name__)

class PublishGmi:

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
                    PublishGmi.page(pathname, filename=filename)
                else:
                    PublishGmi.page(pathname, directory=directory)
        # Generate subsequent files
        for root, directories, filenames in os.walk(directory_source):
            for directory in directories:
                pathname = os.path.join(root, directory)
                directory_output_directory = os.path.join(
                    publish_properties.directory_output, directory)
                if not os.path.exists(directory_output_directory):
                    os.mkdir(directory_output_directory)
                index_file = os.path.join(pathname, "index.rst")
                if os.path.exists(index_file):
                    PublishGmi.pages(pathname, directory, index_file)
                for filename_ in os.listdir(pathname):
                    if filename_ == "index.rst": continue
                    pathname_ = os.path.join(pathname, filename_)
                    directory_output_directory_filename_ = os.path.join(
                        publish_properties.directory_output, directory, filename_[:-4])
                    if not os.path.exists(directory_output_directory_filename_):
                        os.mkdir(directory_output_directory_filename_)
                    if os.path.isfile(pathname_):
                        PublishGmi.page(pathname_, filename=filename_,
                                        directory=directory)
                    elif os.path.isdir(pathname_):
                        print("Warning.")
        #directory_source_posts = publish_properties.directory_source_posts
        #for filename in os.listdir(directory_source_posts):
        #    PublishGmi.page(directory_source_posts, filename=filename, directory="posts")
        #PublishGmi.pages(directory_source_posts, "posts")
        PublishGmi.collection("collection.opml")

    def collection(filename) -> None:
        """Create an OPML Collection"""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{filename}	Start")
        # NOTE /posts and /tags and for PubSub also /categories
        gmi = "# OPML Collection\n"
        gmi += "Rivista Voyager Subscriptions\n"
        identifier = filename[:-5]
        directory_output = publish_properties.directory_output
        for subdirectory in os.listdir(directory_output):
            pathname = os.path.join(directory_output, subdirectory)
            if os.path.isdir(pathname):
                list_of_dirs_and_files = os.listdir(pathname)
                if "index.gmi" in list_of_dirs_and_files:
                    for dir_or_file in list_of_dirs_and_files:
                        pathname_ = os.path.join(pathname, dir_or_file)
                        if os.path.isdir(pathname_):
                            gmi+= f"=> /{subdirectory} {subdirectory}\n" # TODO Extract title from index.atom
                            break
        identifier = filename[:-5]
        directory_output_identifier = os.path.join(directory_output, identifier)
        if not os.path.exists(directory_output_identifier):
            os.mkdir(directory_output_identifier)
        filepath = os.path.join(directory_output_identifier, "index.gmi")
        with open(filepath, "w") as fn: fn.write(gmi)

    def page(pathname, filename="", directory="") -> None:
        """Create a Gemtext document."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{filename}	Start")
        logger.debug(f"{function_name}	{pathname}	Start")
        logger.debug(f"{function_name}	{directory}	Start")
        rst_content_str = open(pathname, mode="r").read()
        xhtml_content_str = UtilityDocument.convert(rst_content_str, "xhtml")
        properties = UtilityRst.properties(rst_content_str)
        # Generate Gemtext
        gmi = publish_properties.gemtext_top
        if properties["title"]:
            gmi += "# " + properties["title"] + "\n\n"
        if properties["summary"]:
            gmi += properties["summary"] + "\n\n"
        gmi += UtilityDocument.convert_rst_to_gmi(rst_content_str) + "\n\n"
        gmi += "# Information\n"
        identifier = filename[:-4] if filename and filename != "index.rst" else ""
        if not identifier == "index":
            gmi += "```Metadata\n"
            if properties["published"]:
                gmi += "Published : " + properties["published"] + "\n"
            if properties["updated"]:
                gmi += "Updated   : " + properties["updated"] + "\n"
            gmi += "```\n"
        properties_link = properties["link"]
        # TODO Select protocol scheme gemini: or type text/gemini
        gmi += f"=> /{directory}/{properties_link}/source.rst Source\n"
        authors = properties["author"]
        properties_authors = UtilityCsv.parse_csv_to_dict(properties["author"])
        if authors:
            gmi+= "## Authors\n"
            for properties_author in properties_authors:
                if "name" in properties_author:
                    # TODO Create an absolute HTTP URL.
                    name = properties_author["name"]
                    address = properties_author["uri"]
                    if address:
                        gmi+= f"=> {address.strip()} {name.strip()}\n"
                    else:
                        gmi+= f"{name.strip()}\n"
        resources = []
        enclosures = []
        navigation = {}
        properties_links = UtilityCsv.parse_csv_to_dict(properties["links"])
        for properties_link in properties_links:
            if "rel" in properties_link and properties_link["rel"] in ("previous", "proceed"):
                if properties_link["rel"] == "proceed":
                    navigation["proceed"] = {
                        "href" : properties_link["href"],
                        "title" : properties_link["title"]}
                if properties_link["rel"] == "previous":
                    navigation["previous"] = {
                        "href" : properties_link["href"],
                        "title" : properties_link["title"]}
            if "href" in properties_link:
                title = properties_link["title"]
                address = properties_link["href"]
                if (not address.startswith("/") and
                    not UtilityUri.has_scheme(address)):
                    address = f"/{directory}/{address}"
                if "rel" in properties_link:
                    if properties_link["rel"] == "enclosure":
                        enclosures.append(f"=> {address} {title}\n")
                    elif properties_link["rel"] == "related":
                        resources.append(f"=> {address} {title}\n")
        if enclosures:
            gmi += "## Enclosures\n"
            for enclosure in enclosures:
                gmi += enclosure
        if resources:
            gmi += "## Resources\n"
            for resource in resources:
                gmi += resource
        properties_categories = properties["category"]
        if properties_categories:
            gmi += "## Tags\n"
            for category in properties_categories.replace("\n","").split(","):
                label = category.strip()
                term = category.lower().strip().replace(" ", "-")
                gmi += f"=> /tag/{term.strip()} {label.strip()}\n"
        if navigation:
            gmi += "# Navigation\n"
            if "proceed" in navigation:
                href = navigation["proceed"]["href"]
                title = navigation["proceed"]["title"]
                gmi+= f"=> /{directory}/{href} {title}\n"
            if "previous" in navigation:
                href = navigation["previous"]["href"]
                title = navigation["previous"]["title"]
                gmi+= f"=> /{directory}/{href} {title}\n"
        gmi += publish_properties.gemtext_bottom
        directory_output = publish_properties.directory_output
        filepath_atom_gmi = os.path.join(
            directory_output, directory, identifier, "index.gmi")
        with open(filepath_atom_gmi, "w") as fn: fn.write(gmi)

    def pages(pathname, directory, index_file="") -> None:
        """Create a Gemini Feed."""
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}	{directory}	Start")
        logger.debug(f"{function_name}	{pathname}	Start")
        if index_file:
            rst_content_str = open(index_file, mode="r").read()
            xhtml_content_str = UtilityDocument.convert(rst_content_str, "xhtml")
            gmi_content_str = UtilityDocument.convert_rst_to_gmi(rst_content_str)
            properties = UtilityRst.properties(rst_content_str)
        else:
            properties = {
                "title" : directory.capitalize(),
                "summary" : f"Recent updates for {directory}"
            }
        # Generate GemText
        gmi = publish_properties.gemtext_top
        gmi += "# " + properties["title"] + "\n\n"
        gmi += properties["summary"] + "\n\n"
        if index_file: gmi += gmi_content_str + "\n\n"
        filenames = os.listdir(pathname)
        if filenames: filenames.sort(reverse=True)
        for filename in filenames:
            if filename == "index.rst": continue
            rst_file = os.path.join(pathname, filename)
            rst_data = open(rst_file, mode="r")
            rst_content_str = rst_data.read()
            xhtml_content_str = UtilityDocument.convert(
                rst_content_str, "xhtml")
            properties = UtilityRst.properties(rst_content_str)
            # GemText
            properties_published = properties["published"][:10]
            properties_title = properties["title"]
            gmi += f"=> {filename[:-4]} {properties_published} {properties_title} \n\n"
            gmi += properties["summary"] + "\n\n"
        # Generate GemText of Atom
        gmi += publish_properties.gemtext_bottom
        directory_output = publish_properties.directory_output
        filepath_atom_gmi = os.path.join(directory_output, directory, "index.gmi")
        with open(filepath_atom_gmi, "w") as fn: fn.write(gmi)
