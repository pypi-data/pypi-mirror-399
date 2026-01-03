<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xml="http://www.w3.org/XML/1998/namespace"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output encoding = "UTF-8"
                indent = "yes"
                media-type = "text/html"
                method = "html"
                version = "5"/>
    <xsl:include href="element-article-concise.xslt"/>
    <xsl:include href="element-base.xslt"/>
    <xsl:include href="element-generator.xslt"/>
    <xsl:include href="element-header.xslt"/>
    <xsl:include href="element-link-symbol.xslt"/>
    <xsl:include href="element-meta.xslt"/>
    <xsl:include href="element-navigation-bar.xslt"/>
    <xsl:include href="element-script.xslt"/>
    <xsl:include href="element-text.xslt"/>
    <xsl:include href="element-title.xslt"/>
    <xsl:include href="elements-a.xslt"/>
    <xsl:include href="elements-link-enclosure.xslt"/>
    <xsl:include href="elements-link-relation.xslt"/>
    <xsl:include href="elements-link-stylesheet.xslt"/>
    <xsl:include href="template-contact.xslt"/>
    <xsl:include href="template-determine-output-escaping.xslt"/>
</xsl:stylesheet>
