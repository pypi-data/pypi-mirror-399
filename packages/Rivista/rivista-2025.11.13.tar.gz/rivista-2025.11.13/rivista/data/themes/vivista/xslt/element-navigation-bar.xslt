<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates a navigation bar. -->
    <xsl:template name="element-navigation-bar">
        <xsl:param name="element"/>
        <xsl:param name="relation"/>
        <xsl:if test="$element">
            <nav id="{$relation}">
                <xsl:for-each select="$element">
                    <xsl:element name="a">
                        <xsl:attribute name="href">
                            <xsl:value-of select="@href"/>
                        </xsl:attribute>
                        <xsl:attribute name="type">
                            <xsl:value-of select="@type"/>
                        </xsl:attribute>
                        <xsl:value-of select="@title"/>
                    </xsl:element>
                </xsl:for-each>
            </nav>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
