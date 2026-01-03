#!/usr/bin/python
# -*- coding: utf-8 -*-

from lxml import etree, html
from rivista.utility.logger import UtilityLogger
import sys

logger = UtilityLogger(__name__)

class UtilityHtml:

    def extract_media(data: str) -> list:
    #def extract_media(url: str, data: str):
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        enclosures = []
        try:
            tree = html.fromstring(data)
        # TODO href which start with "magnet", end with "torrent" ,"ogg", "spx", etc.
            enclosures.extend(tree.xpath("//video[@class=\"enclosure\"]/source/@src"))
            enclosures.extend(tree.xpath("//audio[@class=\"enclosure\"]/source/@src"))
            enclosures.extend(tree.xpath("//object[@class=\"enclosure\"]/@data"))
            enclosures.extend(tree.xpath("//img[@class=\"enclosure\"]/@src"))
            enclosures.extend(tree.xpath("//a[@class=\"enclosure\"]/@href"))
        #enclosures = []
        #for raw_path in urls:
            #enclosures.append(UtilityUri.join_url(url, raw_path))
        except:
            print(data)
        return enclosures

    def remove_html_tags(data: str) -> str:
        function_name = sys._getframe().f_code.co_name
        logger.debug(f"{function_name}		Start")
        parser = etree.HTMLParser()
        tree = etree.fromstring(data, parser)
        if tree:
            cleared = etree.tostring(tree, encoding="unicode", method="text")
            result = cleared.replace("\n\n", "\n")
            return result
