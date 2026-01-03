<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template extracts links of alternate mediums by type. -->
    <xsl:template name="entry-alternate-type">
        <xsl:param name="atom"/>
        <xsl:param name="type"/>
        <xsl:param name="title"/>
        <xsl:if test="atom:link[@rel='alternate' and contains(@type, $type)]">
            <xsl:comment>
                <xsl:text>Entry link (alternate)</xsl:text>
            </xsl:comment>
            <xsl:element name="a">
                <xsl:attribute name="href">
                    <xsl:value-of select="atom:link[@rel='alternate' and contains(@type, $type)]/@href"/>
                </xsl:attribute>
                <xsl:value-of select="$title"/>
            </xsl:element>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
