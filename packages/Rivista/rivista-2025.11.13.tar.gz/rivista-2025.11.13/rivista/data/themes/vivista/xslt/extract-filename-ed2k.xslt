<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This templates extracts filename from a given eDonkey2000 URI string. -->
    <xsl:template name="extract-filename-ed2k">
        <xsl:param name="uri"/>
        <!-- xsl:if test="contains($uri, 'file|')" -->
            <xsl:variable name="uri" select="substring-after($uri,'file|')"/>
        <!-- /xsl:if -->
        <xsl:choose>
            <xsl:when test="contains($uri,'|')">
                <xsl:call-template name="extract-filename-ed2k">
                    <xsl:with-param name="uri" select="substring-before($uri,'|')"/>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$uri"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
</xsl:stylesheet>
