<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates a so called "header" title. -->
    <xsl:template name="element-header">
        <xsl:param name="link-header"/>
        <xsl:param name="logo"/>
        <xsl:if test="$link-header or $logo">
            <header>
                <h1>
                    <xsl:choose>
                        <xsl:when test="string-length($logo) &gt; 0 and string-length($link-header/@href) &gt; 0">
                            <xsl:element name="a">
                                <xsl:attribute name="href">
                                    <xsl:value-of select="$link-header/@href"/>
                                </xsl:attribute>
                                <xsl:attribute name="type">
                                    <xsl:value-of select="$link-header/@type"/>
                                </xsl:attribute>
                                <xsl:attribute name="alt">
                                    <xsl:value-of select="$link-header/@title"/>
                                </xsl:attribute>
                                <xsl:element name="img">
                                    <xsl:attribute name="src">
                                        <xsl:value-of select="$logo"/>
                                    </xsl:attribute>
                                </xsl:element>
                            </xsl:element>
                        </xsl:when>
                        <xsl:when test="string-length($logo) &gt; 0">
                            <xsl:element name="img">
                                <xsl:attribute name="src">
                                    <xsl:value-of select="$logo"/>
                                </xsl:attribute>
                            </xsl:element>
                        </xsl:when>
                        <xsl:when test="string-length($link-header/@href) &gt; 0">
                            <xsl:element name="a">
                                <xsl:attribute name="href">
                                    <xsl:value-of select="$link-header/@href"/>
                                </xsl:attribute>
                                <xsl:attribute name="type">
                                    <xsl:value-of select="$link-header/@type"/>
                                </xsl:attribute>
                                <xsl:value-of select="$link-header/@title"/>
                            </xsl:element>
                        </xsl:when>
                    </xsl:choose>
                </h1>
            </header>
        </xsl:if>
    </xsl:template>
</xsl:stylesheet>
