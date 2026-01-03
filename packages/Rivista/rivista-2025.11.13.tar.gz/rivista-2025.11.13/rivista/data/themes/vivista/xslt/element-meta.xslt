<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2016 - 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates (X)HTML element meta (metadata). -->
    <xsl:template name="element-meta">
        <xsl:param name="name"/>
        <xsl:param name="content"/>
        <xsl:if test="string-length($content) &gt; 0">
            <xsl:element name="meta">
                <xsl:attribute name="name">
                    <xsl:value-of select="$name"/>
                </xsl:attribute>
                <xsl:attribute name="content">
                    <xsl:value-of select="$content"/>
                </xsl:attribute>
            </xsl:element>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
