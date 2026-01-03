<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2016 - 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0"
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:xml="http://www.w3.org/XML/1998/namespace"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/opml">
        <!-- index right-to-left language codes -->
        <!-- TODO http://www.w3.org/TR/xpath/#function-lang -->
        <xsl:variable name="rtl"
                      select="lang[
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
                    <xsl:with-param name="content" select="subtitle"/>
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
                        <xsl:when test="//head/title and not(//head/title='')">
                            <xsl:value-of select="//head/title"/>
                        </xsl:when>
                        <xsl:otherwise>OPML</xsl:otherwise>
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
                    <link id="semitic" href="/css/stylesheet-rtl.css"
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
                <div id="feed">
                    <header>
                        <h1 class="title">
                            <xsl:choose>
                                <xsl:when test="//head/title and not(//head/title='') and count(//outline) &gt; 1">
                                    <xsl:value-of select="//head/title"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>OPML Collection</xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </h1>
                        <h2 class="subtitle">
                            <xsl:choose>
                                <xsl:when test="//head/description and not(//head/description='') and count(//outline) &gt; 1">
                                    <xsl:value-of select="//head/description"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>Outline Processor Markup Language</xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </h2>
                    </header>
                    <xsl:if test="count(//outline) &gt; 1">
                        <section id="menu">
                            <details>
                                <summary>
                                    <xsl:text>Listing </xsl:text>
                                    <xsl:value-of select="count(//outline)"/>
                                    <xsl:text> subscriptions</xsl:text>
                                </summary>
                                <!-- xsl:for-each select="outline[position() &lt;21]" -->
                                <ol>
                                    <xsl:for-each select="//outline[not(position() &gt; 20)]">
                                        <li>
                                            <xsl:element name="a">
                                                <xsl:attribute name="href">
                                                    <xsl:text>#rivista-</xsl:text>
                                                    <xsl:value-of select="position()"/>
                                                </xsl:attribute>
                                                <xsl:choose>
                                                    <xsl:when test="string-length(@text) &gt; 0">
                                                        <xsl:value-of select="@text"/>
                                                    </xsl:when>
                                                    <xsl:otherwise>
                                                        <xsl:text>*** No Title ***</xsl:text>
                                                    </xsl:otherwise>
                                                </xsl:choose>
                                          </xsl:element>
                                        </li>
                                    </xsl:for-each>
                                </ol>
                            </details>
                        </section>
                    </xsl:if>
                    <section id="articles">
                        <!-- opml outline -->
                        <xsl:choose>
                            <xsl:when test="//outline">
                                <xsl:for-each select="//outline[not(position() &gt; 20)]">
                                    <article class="entry h-entry">
                                        <!-- outline title -->
                                        <h3 class="title p-name">
                                            <xsl:element name="a">
                                                <xsl:attribute name="href">
                                                    <xsl:value-of select="@xmlUrl"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="id">
                                                    <xsl:text>rivista-</xsl:text>
                                                    <xsl:value-of select="position()"/>
                                                </xsl:attribute>
                                                <xsl:choose>
                                                    <xsl:when test="string-length(@text) &gt; 0">
                                                        <xsl:value-of select="@text"/>
                                                    </xsl:when>
                                                    <xsl:otherwise>
                                                        <xsl:text>*** No Title ***</xsl:text>
                                                    </xsl:otherwise>
                                                </xsl:choose>
                                            </xsl:element>
                                        </h3>
                                        <h4>
                                            <xsl:value-of select="@text"/>
                                        </h4>
                                        <p class="content">
                                            <xsl:value-of select="@xmlUrl"/>
                                        </p>
                                    </article>
                                </xsl:for-each>
                            </xsl:when>
                            <xsl:otherwise>
                                <article class="notice no-entry"></article>
                            </xsl:otherwise>
                        </xsl:choose>
                    </section>
                </div>
                <xsl:call-template name="element-navigation-bar">
                    <xsl:with-param name="relation" select="'navigation-bottom'"/>
                    <xsl:with-param name="element" select="atom:link[@rel='navigation-bottom']"/>
                </xsl:call-template>
                <!-- Informative note -->
                <xsl:comment>
                    <xsl:text>Informative note</xsl:text>
                </xsl:comment>
                <footer>
                    <xsl:text>This is an OPML Collection document </xsl:text>
                    <xsl:text>which was transformed to HTML with an </xsl:text>
                    <xsl:text>XSLT stylesheet; the collection of </xsl:text>
                    <xsl:text>subscriptions thereof can be imported </xsl:text>
                    <xsl:text>to syndication Feed Readers (also </xsl:text>
                    <xsl:text>referred to as News Reader or RSS </xsl:text>
                    <xsl:text>Reader) which provide automated news </xsl:text>
                    <xsl:text>updates and notifications for desktop </xsl:text>
                    <xsl:text>and mobile devices.</xsl:text>
                </footer>
                <!-- Document generator -->
                <xsl:call-template name="element-generator">
                    <xsl:with-param name="generator" select="atom:generator"/>
                </xsl:call-template>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
