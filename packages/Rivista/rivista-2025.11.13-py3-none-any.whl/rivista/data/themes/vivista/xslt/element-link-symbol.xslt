<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an element link of icon or logo. -->
    <xsl:template name="element-link-symbol">
        <xsl:param name="text"/>
        <xsl:param name="type"/>
        <xsl:if test="string-length($text) &gt; 0">
            <xsl:comment>
                <xsl:text>Document link (</xsl:text>
                <xsl:value-of select="$type"/>
                <xsl:text>) - BEGIN</xsl:text>
            </xsl:comment>
            <xsl:element name="link">
                <xsl:attribute name="href">
                    <xsl:value-of select="$text"/>
                </xsl:attribute>
                <xsl:attribute name="type">
                    <xsl:value-of select="$type"/>
                </xsl:attribute>
            </xsl:element>
            <xsl:comment>
                <xsl:text>Document link (</xsl:text>
                <xsl:value-of select="$type"/>
                <xsl:text>) - END</xsl:text>
            </xsl:comment>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
