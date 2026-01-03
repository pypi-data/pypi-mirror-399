<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates element title. -->
    <xsl:template name="element-title">
        <xsl:param name="document-title"/>
        <xsl:param name="entry-count"/>
        <xsl:param name="entry-title"/>
        <xsl:param name="routine-title"/>
        <h1 class="title p-name">
            <xsl:choose>
                <xsl:when test="string-length($document-title) &gt; 0 and $entry-count &gt; 1">
                    <xsl:comment>
                        <xsl:text>Document title</xsl:text>
                    </xsl:comment>
                    <xsl:value-of select="$document-title"/>
                </xsl:when>
                <xsl:when test="string-length($entry-title) &gt; 0">
                    <xsl:comment>
                        <xsl:text>Entry title</xsl:text>
                    </xsl:comment>
                    <xsl:value-of select="$entry-title"/>
                </xsl:when>
                <xsl:when test="$routine-title">
                </xsl:when>
                <xsl:otherwise>
                    <xsl:text>Untitled</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
        </h1>
    </xsl:template>
</xsl:stylesheet>
