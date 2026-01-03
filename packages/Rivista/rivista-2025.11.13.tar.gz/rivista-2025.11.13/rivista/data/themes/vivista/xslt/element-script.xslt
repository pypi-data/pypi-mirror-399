<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an element script -->
    <xsl:template name="element-script">
        <xsl:param name="links-script"/>
        <xsl:if test="$links-script">
            <xsl:comment>
                <xsl:text>Document link (script) - BEGIN</xsl:text>
            </xsl:comment>
            <xsl:for-each select="$links-script">
                <xsl:element name="script">
                    <xsl:attribute name="src">
                        <xsl:value-of select="@href"/>
                    </xsl:attribute>
                    <xsl:attribute name="type">
                        <xsl:value-of select="@type"/>
                    </xsl:attribute>
                </xsl:element>
            </xsl:for-each>
            <xsl:comment>
                <xsl:text>Document link (script) - END</xsl:text>
            </xsl:comment>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
