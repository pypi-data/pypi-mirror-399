<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates link elements of relation stylesheet. -->
    <xsl:template name="elements-link-stylesheet">
        <xsl:param name="links-stylesheet"/>
        <xsl:if test="$links-stylesheet">
            <xsl:comment>
                <xsl:text>Document link (stylesheet) - BEGIN</xsl:text>
            </xsl:comment>
            <xsl:for-each select="$links-stylesheet">
                <xsl:element name="link">
                    <xsl:attribute name="href">
                        <xsl:value-of select="@href"/>
                    </xsl:attribute>
                    <xsl:if test="contains(@type,'media=')">
                        <xsl:attribute name="media">
                            <xsl:value-of select="normalize-space(substring-after(@type, 'media='))"/>
                        </xsl:attribute>
                    </xsl:if>
                    <xsl:attribute name="rel">
                        <xsl:value-of select="@rel"/>
                    </xsl:attribute>
                    <xsl:attribute name="type">
                        <xsl:choose>
                            <xsl:when test="contains(@type,';')">
                            <xsl:value-of select="normalize-space(substring-before(@type, ';'))"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="@type"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                </xsl:element>
            </xsl:for-each>
            <xsl:comment>
                <xsl:text>Document link (stylesheet) - END</xsl:text>
            </xsl:comment>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
