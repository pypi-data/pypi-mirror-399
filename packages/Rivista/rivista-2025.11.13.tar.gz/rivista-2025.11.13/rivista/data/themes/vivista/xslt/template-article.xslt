<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2016 - 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0" 
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xml="http://www.w3.org/XML/1998/namespace"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/atom:feed">
        <!-- index right-to-left language codes -->
        <!-- TODO http://www.w3.org/TR/xpath/#function-lang -->
        <xsl:variable name="rtl"
                      select="@xml:lang[
                              contains(self::node(),'ar') or 
                              contains(self::node(),'fa') or 
                              contains(self::node(),'he') or 
                              contains(self::node(),'ji') or 
                              contains(self::node(),'ku') or 
                              contains(self::node(),'ur') or 
                              contains(self::node(),'yi')]"/>
        <html>
            <head>
                <xsl:call-template name="element-meta">
                    <xsl:with-param name="name" select="'description'"/>
                    <xsl:with-param name="content" select="atom:subtitle"/>
                </xsl:call-template>
                <xsl:call-template name="element-meta">
                    <xsl:with-param name="name" select="'generator'"/>
                    <xsl:with-param name="content" select="atom:generator"/>
                </xsl:call-template>
                <xsl:if test="atom:category">
                    <xsl:element name="meta">
                        <xsl:attribute name="name">
                            <xsl:text>keywords</xsl:text>
                        </xsl:attribute>
                        <xsl:attribute name="content">
                            <xsl:for-each select="atom:category">
                                <xsl:value-of select="@term"/>
                                <xsl:text>, </xsl:text>
                            </xsl:for-each>
                        </xsl:attribute>
                    </xsl:element>
                </xsl:if>
                <xsl:call-template name="element-meta">
                    <xsl:with-param name="name" select="'mimetype'"/>
                    <xsl:with-param name="content" select="'application/xhtml+xml'"/>
                </xsl:call-template>
                <title>
                    <xsl:choose>
                        <xsl:when test="string-length(atom:title) &gt; 0">
                            <xsl:value-of select="atom:title"/>
                        </xsl:when>
                        <xsl:when test="atom:entry">
                            <xsl:value-of select="atom:entry/atom:title"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:text>Article</xsl:text>
                        </xsl:otherwise>
                    </xsl:choose>
                </title>
                <xsl:call-template name="element-base">
                    <xsl:with-param name="link-self" select="atom:link[@rel='self']"/>
                </xsl:call-template>
                <xsl:call-template name="elements-link-relation">
                    <xsl:with-param name="links-relation" select="atom:link[@rel='alternate']"/>
                    <xsl:with-param name="relation" select="'alternate'"/>
                </xsl:call-template>
                <xsl:call-template name="elements-link-relation">
                    <xsl:with-param name="links-relation" select="atom:link[@rel='search']"/>
                    <xsl:with-param name="relation" select="'search'"/>
                </xsl:call-template>
                <xsl:call-template name="elements-link-relation">
                    <xsl:with-param name="links-relation" select="atom:link[@rel='microsummary']"/>
                    <xsl:with-param name="relation" select="'microsummary'"/>
                </xsl:call-template>
                <xsl:call-template name="element-link-symbol">
                    <xsl:with-param name="text" select="atom:icon"/>
                    <xsl:with-param name="type" select="'icon'"/>
                </xsl:call-template>
                <xsl:call-template name="element-link-symbol">
                    <xsl:with-param name="text" select="atom:logo"/>
                    <xsl:with-param name="type" select="'logo'"/>
                </xsl:call-template>
                <xsl:call-template name="elements-link-stylesheet">
                    <xsl:with-param name="links-stylesheet" select="atom:link[@rel='stylesheet']"/>
                </xsl:call-template>
                <xsl:call-template name="element-script">
                    <xsl:with-param name="links-script" select="atom:link[@rel='script']"/>
                </xsl:call-template>
                <xsl:if test="$rtl">
                    <link href="/css/stylesheet-rtl.css" id="semitic"
                          rel="stylesheet" type="text/css"/>
                </xsl:if>
            </head>
            <body>
                <xsl:call-template name="element-header">
                    <xsl:with-param name="link-header" select="atom:link[@rel='header']"/>
                    <xsl:with-param name="logo" select="atom:logo"/>
                </xsl:call-template>
                <xsl:call-template name="element-navigation-bar">
                    <xsl:with-param name="relation" select="'navigation-top'"/>
                    <xsl:with-param name="element" select="atom:link[@rel='navigation-top']"/>
                </xsl:call-template>
                <div class="h-feed" id="feed">
                    <header>
                        <!-- Document title -->
                        <xsl:call-template name="element-title">
                            <xsl:with-param name="document-title" select="atom:title"/>
                            <xsl:with-param name="entry-count" select="count(atom:entry)"/>
                            <xsl:with-param name="entry-title" select="atom:entry/atom:title"/>
                            <xsl:with-param name="routine-title" select="'Untitled'"/>
                        </xsl:call-template>
                        <!-- Document subtitle -->
                        <xsl:call-template name="element-text">
                            <xsl:with-param name="class" select="'subtitle'"/>
                            <xsl:with-param name="name" select="'subtitle'"/>
                            <xsl:with-param name="routine" select="'Untitled'"/>
                            <xsl:with-param name="tag" select="'h2'"/>
                            <xsl:with-param name="text" select="atom:subtitle"/>
                        </xsl:call-template>
                        <!-- Document summary -->
                        <xsl:if test="string-length(atom:summary) &gt; 0">
                            <xsl:comment>
                                <xsl:text>Entry summary</xsl:text>
                            </xsl:comment>
                            <section class="summary p-summary">
                                <xsl:attribute name="type">
                                    <xsl:value-of select="atom:summary/@type"/>
                                </xsl:attribute>
                                <xsl:copy-of select="atom:summary"/>
                            </section>
                        </xsl:if>
                    </header>
                    <!-- Document entry -->
                    <xsl:comment>
                        <xsl:text>Document entry</xsl:text>
                    </xsl:comment>
                    <section id="articles">
                        <xsl:choose>
                            <xsl:when test="atom:entry">
                                <xsl:for-each select="atom:entry[not(position() &gt; 1)]">
                                    <xsl:call-template name="element-article-content">
                                        <xsl:with-param name="atom" select="atom:entry"/>
                                    </xsl:call-template>
                                </xsl:for-each>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:comment>
                                    <xsl:text>Subject syndication document appears to be empty</xsl:text>
                                </xsl:comment>
                                <article class="entry h-entry">
                                  <h3 class="title">No content</h3>
                                  <h4>This document is empty</h4>
                                  <section class="content">
                                    <xsl:text>Please check that the </xsl:text>
                                    <xsl:text>reStructuredText files </xsl:text>
                                    <xsl:text>are not empty.</xsl:text>
                                  </section>
                                </article>
                            </xsl:otherwise>
                        </xsl:choose>
                    </section>
                </div>
                <!-- External entries -->
                <!--
                  TODO

                  Refer to "element-outsource.xslt".
                  Refer to "element-figure-source.xslt".

                  Check for entries with element "atom:source" and add
                  these as related articles.  These may be local (of
                  Rivista) or external (Blasta, linkhut, et cetera).
                -->
                <xsl:if test="atom:entry/atom:source">
                    <xsl:call-template name="element-outsource">
                        <xsl:with-param name="atom" select="atom:entry"/>
                    </xsl:call-template>
                </xsl:if>
                <xsl:call-template name="element-navigation">
                    <xsl:with-param name="entry-count" select="count(atom:entry)"/>
                    <xsl:with-param name="previous" select="atom:link[@rel='previous']"/>
                    <xsl:with-param name="proceed" select="atom:link[@rel='next']"/>
                </xsl:call-template>
                <xsl:call-template name="element-navigation-bar">
                    <xsl:with-param name="relation" select="'navigation-bottom'"/>
                    <xsl:with-param name="element" select="atom:link[@rel='navigation-bottom']"/>
                </xsl:call-template>
                <!-- Informative note -->
                <xsl:comment>
                    <xsl:text>Informative note</xsl:text>
                </xsl:comment>
                <footer>
                    <xsl:text>This is an Atom Activity Stream </xsl:text>
                    <xsl:text>document which was transformed to HTML </xsl:text>
                    <xsl:text>with an XSLT stylesheet. This document </xsl:text>
                    <xsl:text>can be monitored for changes with </xsl:text>
                    <xsl:text>syndication Feed Readers (also referred </xsl:text>
                    <xsl:text>to as News Reader or RSS Reader) which </xsl:text>
                    <xsl:text>provide automated content updates and </xsl:text>
                    <xsl:text>notifications for desktop and mobile.</xsl:text>
                </footer>
                <!-- Document rights -->
                <xsl:comment>
                    <xsl:text>Feed rights</xsl:text>
                </xsl:comment>
                <xsl:if test="string-length(atom:entry/atom:rights)=0">
                    <footer id="rights">
                        <xsl:copy-of select="atom:rights/text()"/>
                    </footer>
                </xsl:if>
                <!-- Document generator -->
                <xsl:call-template name="element-generator">
                    <xsl:with-param name="generator" select="atom:generator"/>
                </xsl:call-template>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
