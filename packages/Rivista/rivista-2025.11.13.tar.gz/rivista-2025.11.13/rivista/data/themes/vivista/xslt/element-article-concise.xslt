<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an XHTML entry based on content and related resources. -->
    <xsl:template name="element-article-concise">
        <xsl:param name="atom:entry"/>
        <article class="entry h-entry">
            <!-- Summary -->
            <xsl:if test="string-length(atom:summary) &gt; 0">
                <xsl:comment>
                    <xsl:text>Entry summary - BEGIN</xsl:text>
                </xsl:comment>
                <section class="summary p-summary">
                    <xsl:attribute name="type">
                        <xsl:value-of select="atom:summary/@type"/>
                    </xsl:attribute>
                    <xsl:copy-of select="atom:summary"/>
                </section>
                <xsl:comment>
                    <xsl:text>Entry summary - END</xsl:text>
                </xsl:comment>
            </xsl:if>
            <!-- Content -->
            <xsl:if test="string-length(atom:entry/atom:content) &gt; 0">
                <xsl:comment>
                    <xsl:text>Entry content - BEGIN</xsl:text>
                </xsl:comment>
                <section class="content e-content">
                    <xsl:attribute name="type">
                        <xsl:value-of select="atom:entry/atom:content/@type"/>
                    </xsl:attribute>
                    <xsl:copy-of select="atom:entry/atom:content"/>
                </section>
                <xsl:comment>
                    <xsl:text>Entry content - END</xsl:text>
                </xsl:comment>
            </xsl:if>
            <!-- Enclosures -->
            <xsl:call-template name="elements-link-enclosure">
                <xsl:with-param name="links-enclosure" select="atom:link[@rel='enclosure']"/>
            </xsl:call-template>
            <!-- Microsummaries -->
            <xsl:call-template name="elements-a">
                <xsl:with-param name="elements" select="atom:link[@rel='microsummary']"/>
                <xsl:with-param name="kind" select="'microsummary'"/>
                <xsl:with-param name="kind-plural" select="'microsummaries'"/>
                <xsl:with-param name="name" select="'Microsummary'"/>
                <xsl:with-param name="name-plural" select="'Microsummaries'"/>
                <xsl:with-param name="routine" select="'Microsummary'"/>
            </xsl:call-template>
            <!-- Related -->
            <xsl:call-template name="elements-a">
                <xsl:with-param name="elements" select="atom:link[@rel='related']"/>
                <xsl:with-param name="kind" select="'related'"/>
                <xsl:with-param name="kind-plural" select="'relations'"/>
                <xsl:with-param name="name" select="'Related'"/>
                <xsl:with-param name="name-plural" select="'Related'"/>
                <xsl:with-param name="routine" select="'Related'"/>
            </xsl:call-template>
        </article>
    </xsl:template>
</xsl:stylesheet>
