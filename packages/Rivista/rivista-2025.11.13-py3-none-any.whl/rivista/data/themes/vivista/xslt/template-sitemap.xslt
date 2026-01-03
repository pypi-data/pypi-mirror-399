<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0" 
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:sitemap="http://www.sitemaps.org/schemas/sitemap/0.9"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:xml="http://www.w3.org/XML/1998/namespace"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
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
                    <xsl:with-param name="content" select="//atom:generator"/>
                </xsl:call-template>
                <xsl:call-template name="element-meta">
                    <xsl:with-param name="name" select="'mimetype'"/>
                    <xsl:with-param name="content" select="'application/xhtml+xml'"/>
                </xsl:call-template>
                <title>Sitemap</title>
                <xsl:call-template name="element-base">
                    <xsl:with-param name="link-self" select="//atom:link[@rel='self']"/>
                </xsl:call-template>
                <xsl:call-template name="elements-link-relation">
                    <xsl:with-param name="links-relation" select="//atom:link[@rel='alternate']"/>
                    <xsl:with-param name="relation" select="'alternate'"/>
                </xsl:call-template>
                <xsl:call-template name="elements-link-relation">
                    <xsl:with-param name="links-relation" select="//atom:link[@rel='search']"/>
                    <xsl:with-param name="relation" select="'search'"/>
                </xsl:call-template>
                <xsl:call-template name="elements-link-relation">
                    <xsl:with-param name="links-relation" select="//atom:link[@rel='microsummary']"/>
                    <xsl:with-param name="relation" select="'microsummary'"/>
                </xsl:call-template>
                <xsl:call-template name="element-link-symbol">
                    <xsl:with-param name="text" select="//atom:icon"/>
                    <xsl:with-param name="type" select="'icon'"/>
                </xsl:call-template>
                <xsl:call-template name="element-link-symbol">
                    <xsl:with-param name="text" select="//atom:logo"/>
                    <xsl:with-param name="type" select="'logo'"/>
                </xsl:call-template>
                <xsl:call-template name="elements-link-stylesheet">
                    <xsl:with-param name="links-stylesheet" select="//atom:link[@rel='stylesheet']"/>
                </xsl:call-template>
                <xsl:call-template name="element-script">
                    <xsl:with-param name="links-script" select="//atom:link[@rel='script']"/>
                </xsl:call-template>
                <xsl:if test="$rtl">
                    <link id="semitic" href="/css/stylesheet-rtl.css"
                          rel="stylesheet" type="text/css"/>
                </xsl:if>
            </head>
            <body>
                <xsl:call-template name="element-header">
                    <xsl:with-param name="link-header" select="//atom:link[@rel='header']"/>
                    <xsl:with-param name="logo" select="//atom:logo"/>
                </xsl:call-template>
                <xsl:call-template name="element-navigation-bar">
                    <xsl:with-param name="relation" select="'navigation-top'"/>
                    <xsl:with-param name="element" select="//atom:link[@rel='navigation-top']"/>
                </xsl:call-template>
                <div id="feed">
                    <header>
                        <!-- Title -->
                        <h1 class="title">Sitemap</h1>
                        <!-- Subtitle -->
                        <h2 class="subtitle">XML Sitemap</h2>
                    </header>
                    <section id="menu">
                        <details>
                            <xsl:choose>
                                <xsl:when test="count(sitemap:sitemapindex/sitemap:sitemap) &gt; 0">
                                    <summary>
                                        <xsl:text>Listing </xsl:text>
                                        <xsl:copy-of select="count(sitemap:sitemapindex/sitemap:sitemap)"/>
                                        <xsl:text> sitemaps</xsl:text>
                                    </summary>
                                    <!-- xsl:for-each select="sitemap[position() &lt;21]" -->
                                    <ol>
                                        <xsl:for-each select="sitemap:sitemapindex/sitemap:sitemap">
                                            <li>
                                                <xsl:element name="a">
                                                    <xsl:attribute name="href">
                                                        <xsl:text>#rivista-</xsl:text>
                                                        <xsl:copy-of select="position()"/>
                                                    </xsl:attribute>
                                                    <xsl:copy-of select="sitemap:loc"/>
                                              </xsl:element>
                                            </li>
                                        </xsl:for-each>
                                    </ol>
                                </xsl:when>
                                <xsl:when test="count(sitemap:urlset/sitemap:url) &gt; 0">
                                    <summary>
                                        <xsl:text>Listing </xsl:text>
                                        <xsl:copy-of select="count(sitemap:urlset/sitemap:url)"/>
                                        <xsl:text> pages</xsl:text>
                                    </summary>
                                    <!-- xsl:for-each select="sitemap[position() &lt;21]" -->
                                    <ol>
                                        <xsl:for-each select="sitemap:urlset/sitemap:url">
                                            <li>
                                                <xsl:element name="a">
                                                    <xsl:attribute name="href">
                                                        <xsl:text>#rivista-</xsl:text>
                                                        <xsl:copy-of select="position()"/>
                                                    </xsl:attribute>
                                                    <xsl:copy-of select="sitemap:loc"/>
                                              </xsl:element>
                                            </li>
                                        </xsl:for-each>
                                    </ol>
                                </xsl:when>
                            </xsl:choose>
                        </details>
                    </section>
                    <section id="articles">
                        <xsl:choose>
                            <!-- sitemapindex -->
                            <xsl:when test="count(sitemap:sitemapindex/sitemap:sitemap) &gt; 0">
                                <xsl:for-each select="sitemap:sitemapindex/sitemap:sitemap">
                                    <article class="entry h-entry">
                                        <!-- sitemap title -->
                                        <h3 class="title p-name">
                                            <xsl:element name="a">
                                                <xsl:attribute name="href">
                                                    <xsl:copy-of select="sitemap:loc"/>
                                                    <xsl:text>/urlset.xml</xsl:text>
                                                </xsl:attribute>
                                                <xsl:attribute name="id">
                                                    <xsl:text>rivista-</xsl:text>
                                                    <xsl:copy-of select="position()"/>
                                                </xsl:attribute>
                                                <xsl:choose>
                                                    <xsl:when test="string-length(sitemap:lastmod) &gt; 0">
                                                        <xsl:copy-of select="sitemap:lastmod"/>
                                                    </xsl:when>
                                                    <xsl:otherwise>
                                                        <xsl:text>*** No Title ***</xsl:text>
                                                    </xsl:otherwise>
                                                </xsl:choose>
                                            </xsl:element>
                                        </h3>
                                        <h4>
                                            <xsl:copy-of select="sitemap:lastmod"/>
                                        </h4>
                                        <p class="content">
                                            <xsl:copy-of select="sitemap:loc"/>
                                        </p>
                                    </article>
                                </xsl:for-each>
                            </xsl:when>
                            <!-- urlset -->
                            <xsl:when test="count(sitemap:urlset/sitemap:url) &gt; 0">
                                <xsl:for-each select="sitemap:urlset/sitemap:url">
                                    <article class="entry h-entry">
                                        <!-- urlset title -->
                                        <h3 class="title p-name">
                                            <xsl:element name="a">
                                                <xsl:attribute name="href">
                                                    <xsl:copy-of select="sitemap:loc"/>
                                                </xsl:attribute>
                                                <xsl:attribute name="id">
                                                    <xsl:text>rivista-</xsl:text>
                                                    <xsl:copy-of select="position()"/>
                                                </xsl:attribute>
                                                <xsl:choose>
                                                    <xsl:when test="string-length(sitemap:lastmod) &gt; 0">
                                                        <xsl:copy-of select="sitemap:lastmod"/>
                                                    </xsl:when>
                                                    <xsl:otherwise>
                                                        <xsl:text>*** No Title ***</xsl:text>
                                                    </xsl:otherwise>
                                                </xsl:choose>
                                            </xsl:element>
                                        </h3>
                                        <h4>
                                            <xsl:copy-of select="sitemap:lastmod"/>
                                        </h4>
                                        <p class="content">
                                            <xsl:copy-of select="sitemap:loc"/>
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
                    <xsl:with-param name="element" select="//atom:link[@rel='navigation-bottom']"/>
                </xsl:call-template>
                <!-- Informative note -->
                <footer>
                    <xsl:text>This is an XML Sitemap document which </xsl:text>
                    <xsl:text>was transformed to HTML with an XSLT </xsl:text>
                    <xsl:text>stylesheet; the list of links thereof </xsl:text>
                    <xsl:text>is meant for consumption by indexers </xsl:text>
                    <xsl:text>and for HTML browsers, as well as any </xsl:text>
                    <xsl:text>other software which is able to parse </xsl:text>
                    <xsl:text>XML files to map and navigate sites.</xsl:text>
                </footer>
                <!-- Document generator -->
                <xsl:call-template name="element-generator">
                    <xsl:with-param name="generator" select="//atom:generator"/>
                </xsl:call-template>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
