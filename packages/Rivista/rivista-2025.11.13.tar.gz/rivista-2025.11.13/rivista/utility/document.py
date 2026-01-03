#!/usr/bin/python
# -*- coding: utf-8 -*-

from docutils.core import publish_parts
import rst2gemtext

class UtilityDocument:

    def convert_rst_to_gmi(rst_content_str):
        return rst2gemtext.convert(rst_content_str)

    def convert(rst_content_str, filetype):
        html_content_str = publish_parts(source=rst_content_str,
                                         writer_name=filetype)
        #return html_content_str["fragment"]
        return html_content_str["html_body"]
