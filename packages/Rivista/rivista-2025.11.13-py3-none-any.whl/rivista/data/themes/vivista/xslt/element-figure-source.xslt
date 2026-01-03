<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This templates creates an XHTML entry based on its title and summary. -->
    <xsl:template name="element-figure-source">
        <xsl:param name="atom"/>
        <xsl:comment>
            <xsl:text>Document entry - BEGIN</xsl:text>
        </xsl:comment>
        <figure class="entry h-entry">
            <xsl:attribute name="id">
                <xsl:value-of select="atom:id"/>
            </xsl:attribute>
            <xsl:attribute name="title">
                <!-- Subtitle -->
                <xsl:call-template name="element-text">
                    <xsl:with-param name="class" select="'title p-name'"/>
                    <xsl:with-param name="name" select="'title'"/>
                    <xsl:with-param name="routine" select="'(No summmary)'"/>
                    <xsl:with-param name="tag" select="'span'"/>
                    <xsl:with-param name="text" select="concat(atom:summary, ' - ', substring(atom:published,0,11))"/>
                </xsl:call-template>
            </xsl:attribute>
            <!-- Image -->
            <xsl:variable name="link-enclosure-image" select="atom:link[@rel='enclosure' and starts-with(@type,'image/')]"/>
            <xsl:if test="$link-enclosure-image">
                <xsl:comment>
                    <xsl:text>Entry link (enclosure)</xsl:text>
                </xsl:comment>
                <xsl:call-template name="element-image">
                    <xsl:with-param name="alt" select="$link-enclosure-image/@title"/>
                    <xsl:with-param name="src" select="$link-enclosure-image/@href"/>
                    <!-- xsl:with-param name="title" select="$link-enclosure-image/@title"/ -->
                    <xsl:with-param name="type" select="$link-enclosure-image/@type"/>
                </xsl:call-template>
            </xsl:if>
            <!-- Title -->
            <figcaption>
                <xsl:attribute name="id">
                     <xsl:value-of select="atom:id"/>
                </xsl:attribute>
                <xsl:element name="a">
                    <xsl:attribute name="href">
                        <xsl:choose>
                            <xsl:when test="atom:link[@rel='self']">
                                <xsl:value-of select="atom:link[@rel='self']/@href"/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:value-of select="atom:link/@href"/>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:attribute>
                    <xsl:call-template name="element-text">
                        <xsl:with-param name="class" select="'title p-name'"/>
                        <xsl:with-param name="name" select="'title'"/>
                        <xsl:with-param name="routine" select="'Untitled'"/>
                        <xsl:with-param name="tag" select="'span'"/>
                        <xsl:with-param name="text" select="atom:title"/>
                    </xsl:call-template>
                </xsl:element>
            </figcaption>
        </figure>
        <xsl:comment>
            <xsl:text>Document entry - END</xsl:text>
        </xsl:comment>
    </xsl:template>
</xsl:stylesheet>
