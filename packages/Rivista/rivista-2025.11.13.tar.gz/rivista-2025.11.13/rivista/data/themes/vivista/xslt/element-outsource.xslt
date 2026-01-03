<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- This template creates an XHTML entry, based on properties, content, and related resources. -->
    <xsl:template name="element-outsource">
        <xsl:param name="atom"/>
        <xsl:comment>
            <xsl:text>Document entry (source) - BEGIN</xsl:text>
        </xsl:comment>
        <div id="related">
            <xsl:for-each select="atom:entry/atom:source">
                <xsl:call-template name="element-outsource">
                    <xsl:with-param name="source-author" select="atom:entry/atom:source/atom:author"/>
                    <xsl:with-param name="source-contributor" select="atom:entry/atom:source/atom:contributor"/>
                    <xsl:with-param name="source-icon" select="atom:entry/atom:source/atom:icon"/>
                    <xsl:with-param name="source-id" select="atom:entry/atom:source/atom:id"/>
                    <xsl:with-param name="source-logo" select="atom:entry/atom:source/atom:logo"/>
                    <xsl:with-param name="source-title" select="atom:entry/atom:source/atom:title"/>
                    <xsl:with-param name="source-updated" select="atom:entry/atom:source/atom:updated"/>
                    <xsl:with-param name="summary" select="atom:entry/atom:summary"/>
                    <xsl:with-param name="title" select="atom:entry/atom:title"/>
                </xsl:call-template>
            </xsl:for-each>
            <article class="entry h-entry">
                <!--
                  TODO

                  Refer to "element-figure-source.xslt".

                  * Retrieve text of atom:author, atom:summary and atom:updated
                    or atom:published;
                  * Parse HTML of atom:summary;
                  * Shorten text of atom:summary;
                  * Join text of Author, Summary, and Date;
                  
                  atom:entry/atom:source/atom:author
                  substring(atom:updated,0,11) or substring(atom:published,0,11)
                  atom:summary
                -->
                <!-- Figure -->
                <xsl:variable name="link-enclosure-image" select="atom:link[@rel='enclosure' and starts-with(@type,'image/')]"/>
                <xsl:if test="$link-enclosure-image">
                    <xsl:comment>
                        <xsl:text>Entry link (enclosure)</xsl:text>
                    </xsl:comment>
                    <xsl:call-template name="element-figure">
                        <xsl:with-param name="alt" select="$link-enclosure-image/@title"/>
                        <xsl:with-param name="src" select="$link-enclosure-image/@href"/>
                        <xsl:with-param name="title" select="$link-enclosure-image/@title"/>
                        <xsl:with-param name="type" select="$link-enclosure-image/@type"/>
                    </xsl:call-template>
                </xsl:if>
                <!-- Summary -->
                <xsl:if test="string-length(atom:summary) &gt; 0">
                    <xsl:comment>
                        <xsl:text>Entry summary</xsl:text>
                    </xsl:comment>
                    <section class="summary e-summary">
                        <xsl:attribute name="type">
                            <xsl:value-of select="atom:summary/@type"/>
                        </xsl:attribute>
                        <xsl:copy-of select="atom:summary"/>
                    </section>
                </xsl:if>
                <!-- Tags -->
                <xsl:call-template name="element-tags">
                    <xsl:with-param name="category" select="atom:category"/>
                </xsl:call-template>
            </article>
        </div>
        <xsl:comment>
            <xsl:text>Document entry (source) - END</xsl:text>
        </xsl:comment>
    </xsl:template>
</xsl:stylesheet>
