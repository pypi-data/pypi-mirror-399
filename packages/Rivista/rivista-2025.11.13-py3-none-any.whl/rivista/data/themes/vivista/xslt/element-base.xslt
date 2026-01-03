<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- Set an (X)HTML element base -->
    <xsl:template name="element-base">
        <xsl:param name="link-self"/>
        <xsl:if test="$link-self">
            <xsl:comment>
                <xsl:text>Document link (self) - BEGIN</xsl:text>
            </xsl:comment>
            <xsl:element name="base">
                <xsl:attribute name="href">
                    <xsl:value-of select="$link-self/@href"/>
                </xsl:attribute>
            </xsl:element>
            <xsl:comment>
                <xsl:text>Document link (self) - END</xsl:text>
            </xsl:comment>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
