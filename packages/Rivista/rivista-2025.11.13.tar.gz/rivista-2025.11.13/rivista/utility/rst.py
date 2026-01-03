#!/usr/bin/python
# -*- coding: utf-8 -*-

import docutils.nodes
import docutils.parsers.rst
import docutils.utils
import docutils.frontend

class UtilityRst:

    def properties(rst_content_str: str) -> dict:
        parser = docutils.parsers.rst.Parser()
        components = (docutils.parsers.rst.Parser,)
        settings = docutils.frontend.OptionParser(components=components).get_default_values()
        document = docutils.utils.new_document("<rst-doc>", settings=settings)
        parser.parse(rst_content_str, document)
        # TODO Move this to UtilityProprties.
        properties = {
            "author"         : "",
            "category"       : "",
            "comments"       : "",
            "contributor"    : "",
            "id"             : "",
            "lang"           : "",
            "link"           : "",
            "links"          : "",
            "published"      : "",
            "rights"         : "",
            "source" : {
                "link"   : "",
                "links"  : "",
                "rights" : "",
                "title"  : ""
            },
            "subtitle"        : "",
            "summary"        : "",
            "title"          : "",
            "type"           : "",
            "updated"        : ""}
        for property in properties:
            for line in document.traverse():
                line_str = line.astext()
                if line_str.startswith(f"{property}:"):
                    content = line_str.split(":")
                    content.pop(0)
                    content_str = ":".join(content)
                    properties[property] = content_str.strip()
        return properties

    def value_of_metadata(rst_content_str, key):
        lines = rst_content_str.split("\n")
        for line in lines:
            if line.startswith(f".. {key}"):
                value = line.split(": ")[1]
                return value
