<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template extracts links of alternate mediums by scheme. -->
    <xsl:template name="entry-alternate-scheme">
        <xsl:param name="atom"/>
        <xsl:param name="scheme"/>
        <xsl:param name="title"/>
        <xsl:if test="atom:link[@rel='alternate' and starts-with(@href, $scheme)]">
            <xsl:comment>
                <xsl:text>Entry link (alternate)</xsl:text>
            </xsl:comment>
            <xsl:element name="a">
                <xsl:attribute name="href">
                    <xsl:value-of select="atom:link[@rel='alternate' and starts-with(@href, $scheme)]/@href"/>
                </xsl:attribute>
                <xsl:value-of select="$title"/>
            </xsl:element>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
