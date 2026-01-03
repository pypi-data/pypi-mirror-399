<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an (X)HTML element. -->
    <xsl:template name="element-text">
        <xsl:param name="id"/>
        <xsl:param name="class"/>
        <xsl:param name="name"/>
        <xsl:param name="routine"/>
        <xsl:param name="tag"/>
        <xsl:param name="text"/>
        <xsl:comment>
            <xsl:text>Entry </xsl:text>
            <xsl:value-of select="$name"/>
            <xsl:text> - BEGIN</xsl:text>
        </xsl:comment>
        <xsl:element name="{$tag}">
            <xsl:attribute name="class">
                <xsl:value-of select="$class"/>
            </xsl:attribute>
            <xsl:attribute name="id">
                <xsl:value-of select="$id"/>
            </xsl:attribute>
            <xsl:choose>
                <xsl:when test="string-length($text) &gt; 0">
                    <xsl:value-of select="$text"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$routine"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:element>
        <xsl:comment>
            <xsl:text>Entry </xsl:text>
            <xsl:value-of select="$name"/>
            <xsl:text> - END</xsl:text>
        </xsl:comment>
    </xsl:template>
</xsl:stylesheet>
