<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:thr="http://purl.org/syndication/thread/1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template extracts link of replies. -->
    <xsl:template name="entry-link-replies">
        <xsl:param name="link"/>
        <xsl:param name="title"/>
        <xsl:element name="a">
            <xsl:attribute name="href">
                <xsl:value-of select="@href"/>
                <!-- xsl:value-of select="@thr:count"/ -->
            </xsl:attribute>
            <xsl:value-of select="$title"/>
        </xsl:element>
    </xsl:template>
</xsl:stylesheet>
