<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an element of published. -->
    <xsl:template name="element-published">
        <xsl:param name="timestamp"/>
        <xsl:comment>
            <xsl:text>Entry published - BEGIN</xsl:text>
        </xsl:comment>
        <span class="published dt-published">
            <xsl:choose>
                <xsl:when test="string-length($timestamp) &gt; 0">
                    <xsl:attribute name="title">
                        <xsl:value-of select="$timestamp"/>
                    </xsl:attribute>
                    <xsl:value-of select="substring($timestamp,0,11)"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:attribute name="title">
                        <xsl:text>No publishing date is specified for this entry.</xsl:text>
                    </xsl:attribute>
                    <xsl:text>Unknown</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
        </span>
        <xsl:comment>
            <xsl:text>Entry published - END</xsl:text>
        </xsl:comment>
    </xsl:template>
</xsl:stylesheet>
