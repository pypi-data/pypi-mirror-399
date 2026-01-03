<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0" 
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
                xmlns:xlink="http://www.w3.org/1999/xlink"
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
                <xsl:call-template name="element-meta">
                    <xsl:with-param name="name" select="'mimetype'"/>
                    <xsl:with-param name="content" select="'application/xhtml+xml'"/>
                </xsl:call-template>
                <title>
                    <xsl:choose>
                        <xsl:when test="string-length(atom:title) &gt; 0">
                            <xsl:value-of select="atom:title"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:text>Search</xsl:text>
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
                            <xsl:with-param name="routine-title" select="'Search'"/>
                        </xsl:call-template>
                        <!-- Document subtitle -->
                        <xsl:call-template name="element-text">
                            <xsl:with-param name="class" select="'subtitle'"/>
                            <xsl:with-param name="name" select="'subtitle'"/>
                            <xsl:with-param name="routine" select="'Untitled'"/>
                            <xsl:with-param name="tag" select="'h2'"/>
                            <xsl:with-param name="text" select="atom:subtitle"/>
                        </xsl:call-template>
                    </header>
                    <section id="search">
                        <form action="/search/" method="post">
                            <dl>
                                <dt>
                                    <label for="query">Query:</label>
                                </dt>
                                <dd>
                                    <input autofocus=""
                                           id="query"
                                           name="query"
                                           placeholder="Query"
                                           required=""
                                           type="text"/>
                                </dd>
                                <!-- dt>
                                    <span>Parameters:</span>
                                </dt -->
                                <dd>
                                    <!-- span>
                                        <input id="search-author"
                                               name="author"
                                               type="checkbox"
                                               value="yes"/>
                                        <label for="search-author">Author</label>
                                    </span -->
                                    <span>
                                        <input id="search-content"
                                               name="content"
                                               type="checkbox"
                                               value="yes"/>
                                        <label for="search-content">Content</label>
                                    </span>
                                    <!-- span>
                                        <input id="search-link"
                                               name="link"
                                               type="checkbox"
                                               value="yes"/>
                                        <label for="search-link">Link</label>
                                    </span -->
                                    <span>
                                        <input id="search-summary"
                                               name="summary"
                                               type="checkbox"
                                               value="yes"/>
                                        <label for="search-summary">Summary</label>
                                    </span>
                                    <span>
                                        <input id="search-title"
                                               name="title"
                                               type="checkbox"
                                               value="yes"/>
                                        <label for="search-title">Title</label>
                                    </span>
                                </dd>
                            </dl>
                            <div>
                                <button type="submit">Proceed</button>
                            </div>
                        </form>
                    </section>
                    <!-- Table of contents -->
                    <xsl:call-template name="element-menu">
                        <!-- xsl:with-param name="atom:entry[position() &lt;21]" -->
                        <xsl:with-param name="links" select="atom:entry[not(position() &gt; 20)]"/>
                        <xsl:with-param name="type" select="' results'"/>
                    </xsl:call-template>
                    <xsl:if test="atom:entry">
                        <section id="articles">
                            <xsl:for-each select="atom:entry[not(position() &gt; 20)]">
                                <span>
                                    <xsl:attribute name="id">
                                        <xsl:text>result-</xsl:text>
                                        <xsl:value-of select="position()"/>
                                    </xsl:attribute>
                                </span>
                                <xsl:call-template name="element-article-summary">
                                    <xsl:with-param name="atom" select="atom:entry"/>
                                </xsl:call-template>
                            </xsl:for-each>
                        </section>
                    </xsl:if>
                </div>
                <xsl:call-template name="element-navigation">
                    <xsl:with-param name="entry-count" select="count(atom:entry)"/>
                    <xsl:with-param name="previous" select="atom:link[@rel='previous']"/>
                    <xsl:with-param name="proceed" select="atom:link[@rel='next']"/>
                </xsl:call-template>
                <xsl:call-template name="element-navigation-bar">
                    <xsl:with-param name="relation" select="'navigation-bottom'"/>
                    <xsl:with-param name="element" select="atom:link[@rel='navigation-bottom']"/>
                </xsl:call-template>
                <!-- note -->
                <footer>
                    <xsl:text>This is an Atom Syndication Format </xsl:text>
                    <xsl:text>document which was transformed </xsl:text>
                    <xsl:text>to HTML with an XSLT </xsl:text>
                    <xsl:text>stylesheet. This document can be </xsl:text>
                    <xsl:text>viewed with syndication Feed </xsl:text>
                    <xsl:text>Readers (also referred to as </xsl:text>
                    <xsl:text>News Reader or RSS Reader) </xsl:text>
                    <xsl:text>which provide automated content </xsl:text>
                    <xsl:text>updates and notifications for </xsl:text>
                    <xsl:text>desktop and mobile devices.</xsl:text>
                </footer>
                <xsl:if test="string-length(atom:rights) &gt; 0 and count(atom:entry) &gt; 1 or string-length(atom:entry/atom:rights)=0">
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
