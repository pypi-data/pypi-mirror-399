<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an element of updated. -->
    <xsl:template name="element-updated">
        <xsl:param name="timestamp"/>
        <xsl:comment>
            <xsl:text>Entry updated - BEGIN</xsl:text>
        </xsl:comment>
        <xsl:if test="string-length($timestamp) &gt; 0">
            <span> Updated: </span>
            <span class="updated dt-updated">
                <xsl:attribute name="title">
                    <xsl:value-of select="$timestamp"/>
                </xsl:attribute>
                <xsl:value-of select="substring($timestamp,0,11)"/>
            </span>
        </xsl:if>
        <xsl:comment>
            <xsl:text>Entry updated - END</xsl:text>
        </xsl:comment>
    </xsl:template>
</xsl:stylesheet>
