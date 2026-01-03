<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates link elements of a given relation. -->
    <xsl:template name="elements-link-relation">
        <xsl:param name="links-relation"/>
        <xsl:param name="relation"/>
        <xsl:if test="$links-relation">
            <xsl:comment>
                <xsl:text>Document link (</xsl:text>
                <xsl:value-of select="$relation"/>
                <xsl:text>) - BEGIN</xsl:text>
            </xsl:comment>
            <xsl:for-each select="$links-relation">
                <xsl:element name="link">
                    <xsl:attribute name="href">
                        <xsl:value-of select="@href"/>
                    </xsl:attribute>
                    <xsl:attribute name="title">
                        <xsl:value-of select="@title"/>
                    </xsl:attribute>
                    <xsl:attribute name="rel">
                        <xsl:value-of select="@rel"/>
                    </xsl:attribute>
                    <xsl:attribute name="type">
                        <xsl:value-of select="@type"/>
                    </xsl:attribute>
                </xsl:element>
            </xsl:for-each>
            <xsl:comment>
                <xsl:text>Document link (</xsl:text>
                <xsl:value-of select="$relation"/>
                <xsl:text>) - END</xsl:text>
            </xsl:comment>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
