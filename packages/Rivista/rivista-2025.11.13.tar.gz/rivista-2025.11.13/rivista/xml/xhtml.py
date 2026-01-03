#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import xml.etree.ElementTree as ET

class XmlXhtml:

    def generate_xhtml(atom: dict):
        """Generate an XHTML document."""
        e_html = ET.Element('html')
        e_html.set('xmlns', 'http://www.w3.org/1999/xhtml')
        e_head = ET.SubElement(e_html, 'head')
        ET.SubElement(e_head, 'title').text = atom['title']
        ET.SubElement(e_head, 'link', {'rel': 'stylesheet',
                                       'href': 'pubsub.css'})
        e_body = ET.SubElement(e_html, "body")
        ET.SubElement(e_body, "h1").text = atom['title']
        ET.SubElement(e_body, "h2").text = atom['subtitle']
        for item in atom['items']:
            item_id = item['id']
            title = item['title']
            links = item['links']
            e_article = ET.SubElement(e_body, 'article')
            e_title = ET.SubElement(e_article, 'h3')
            e_title.text = item['title']
            e_title.set('id', item['id'])
            e_date = ET.SubElement(e_article, 'h4')
            e_date.text = item['published']
            e_date.set('title', 'Updated: ' + item['updated'])
            authors = item['authors']
            if authors:
                e_authors = ET.SubElement(e_article, "dl")
                ET.SubElement(e_authors, "dt").text = 'Authors'
                for author in authors:
                    e_dd = ET.SubElement(e_authors, 'dd')
                    e_author = ET.SubElement(e_dd, 'a')
                    e_author.text = author['name'] or author['uri'] or author['email']
                    if 'email' in author and author['email']:
                        e_author.set('href', 'mailto:' + author['email'])
                    elif 'uri' in author and author['uri']:
                        e_author.set('href', author['uri'])
            for content in item['contents']:
                ET.SubElement(e_article, 'p', {'type': content['type']}).text = content['text']
            if links:
                e_links = ET.SubElement(e_article, "dl")
                e_links.set('class', 'links')
                ET.SubElement(e_links, "dt").text = 'Links'
                for link in links:
                    e_dd = ET.SubElement(e_links, 'dd')
                    e_link = ET.SubElement(e_dd, 'a')
                    e_link.set('href', link['href'])
                    e_link.text = link['rel']
                    if link['type']: ET.SubElement(e_dd, 'span').text = link['type']
            categories = item['categories']
            if categories:
                e_categories = ET.SubElement(e_article, "dl")
                e_categories.set('class', 'categories')
                ET.SubElement(e_categories, "dt").text = 'Categories'
                for category in categories:
                    ET.SubElement(e_categories, 'dd').text = category
        return ET.tostring(e_html, encoding='unicode')
