<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template extract software information. -->
    <xsl:template name="element-generator">
        <xsl:param name="generator"/>
        <xsl:if test="string-length($generator) &gt; 0">
            <footer id="generator">
                <xsl:text>Powered by </xsl:text>
                <xsl:comment>
                    <xsl:text>Document generator - BEGIN</xsl:text>
                </xsl:comment>
                <a>
                    <xsl:attribute name="href">
                        <xsl:value-of select="$generator/@uri"/>
                    </xsl:attribute>
                    <xsl:attribute name="title">
                        <xsl:value-of select="$generator/@version"/>
                    </xsl:attribute>
                    <xsl:value-of select="$generator"/>
                </a>
                <xsl:comment>
                    <xsl:text>Theme - BEGIN</xsl:text>
                </xsl:comment>
                <span title="2025.12.21"> and Vivista</span>
                <xsl:comment>
                    <xsl:text>Document generator - END</xsl:text>
                </xsl:comment>
            </footer>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
