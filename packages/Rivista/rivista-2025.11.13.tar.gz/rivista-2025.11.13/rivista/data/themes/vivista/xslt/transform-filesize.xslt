<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2016 - 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- transform filesize from given length string -->
    <xsl:template name="transform-filesize">
        <xsl:param name="length"/>
        <!-- TODO consider xsl:decimal-format and xsl:number -->
        <xsl:choose>
            <!-- TODO consider removal of Byte -->
            <xsl:when test="$length &lt; 2">
                <xsl:value-of select="$length"/>
                <xsl:text>Byte</xsl:text>
            </xsl:when>
            <xsl:when test="floor($length div 1024) &lt; 1">
                <xsl:value-of select="$length"/>
                <xsl:text>Bytes</xsl:text>
            </xsl:when>
            <xsl:when test="floor($length div (1024 * 1024)) &lt; 1">
                <xsl:value-of select="floor($length div 1024)"/>.<xsl:value-of select="substring($length mod 1024,0,2)"/>
                <xsl:text>KiB</xsl:text>
            </xsl:when>
            <xsl:when test="floor($length div (1024 * 1024 * 1024)) &lt; 1">
                <xsl:value-of select="floor($length div (1024 * 1024))"/>.<xsl:value-of select="substring($length mod (1024 * 1024),0,2)"/>
                <xsl:text>MiB</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <!-- P2P links -->
                <xsl:value-of select="floor($length div (1024 * 1024 * 1024))"/>.<xsl:value-of select="substring($length mod (1024 * 1024 * 1024),0,2)"/>
                <xsl:text>GiB</xsl:text>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>
