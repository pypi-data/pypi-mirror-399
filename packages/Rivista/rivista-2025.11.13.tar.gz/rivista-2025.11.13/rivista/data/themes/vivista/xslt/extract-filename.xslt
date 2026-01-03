<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2016 - 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This templates extracts filename from a given IRI (URI or URL) string. -->
    <xsl:template name="extract-filename">
        <xsl:param name="uri"/>
        <xsl:choose>
            <xsl:when test="contains($uri,'/')">
                <xsl:call-template name="extract-filename">
                    <xsl:with-param name="uri" select="substring-after($uri,'/')"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$uri"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>
