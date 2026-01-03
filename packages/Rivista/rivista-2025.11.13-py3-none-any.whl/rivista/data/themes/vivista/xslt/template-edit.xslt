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
                <title>
                    <xsl:choose>
                        <xsl:when test="string-length(atom:title) &gt; 0">
                            <xsl:text>Editor: </xsl:text>
                            <xsl:value-of select="atom:title"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:text>Editor</xsl:text>
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
                <div class="h-feed" id="feed">
                    <header>
                        <!-- page title -->
                        <h1 id="title">Editor</h1>
                        <!-- feed title -->
                        <h2 id="subtitle">
                            <xsl:choose>
                                <xsl:when test="string-length(atom:title) &gt; 0">
                                    <xsl:value-of select="atom:title"/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text>Untitled</xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </h2>
                    </header>
                    <section id="articles">
                        <!-- feed entry -->
                        <xsl:choose>
                            <xsl:when test="atom:entry">
                                <xsl:for-each select="atom:entry[not(position() &gt; 1)]">
                                    <article class="entry h-entry">
                                     <form action="/save" method="post">
                                        <!-- edit document -->
                                        <xsl:if test="string-length(atom:content) &gt; 0">
                                            <h4>Source</h4>
                                            <textarea class="content e-content" rows="30">
                                                <xsl:value-of select="atom:content"/>
                                            </textarea>
                                        </xsl:if>
                                        <!-- entry tags -->
                                        <xsl:if test="atom:category">
                                            <h4>Tags</h4>
                                            <input class="tags" type="text">
                                                <xsl:attribute name="value">
                                                    <xsl:for-each select="atom:category">
                                                        <xsl:value-of select="@term"/>
                                                        <xsl:text>, </xsl:text>
                                                    </xsl:for-each>
                                                </xsl:attribute>
                                            </input>
                                        </xsl:if>
                                        <!-- entry enclosure -->
                                        <xsl:if test="atom:link[@rel='enclosure']">
                                            <h4>Media</h4>
                                            <section class="enclosures">
                                                <xsl:for-each select="atom:link[@rel='enclosure']">
                                                    <div>
                                                        <xsl:attribute name="class">
                                                            <xsl:value-of select="substring-before(@type,'/')"/>
                                                            <xsl:text> enclosure</xsl:text>
                                                        </xsl:attribute>
                                                        <xsl:element name="a">
                                                            <xsl:attribute name="href">
                                                                <xsl:value-of select="@href"/>
                                                            </xsl:attribute>
                                                            <xsl:attribute name="download"/>
                                                            <!-- xsl:call-template name="extract-filename">
                                                                <xsl:with-param name="url" select="@href"/>
                                                            </xsl:call-template -->
                                                        </xsl:element>
                                                        <!-- xsl:if test="@length &gt; 0">
                                                            <xsl:call-template name="transform-filesize">
                                                                <xsl:with-param name="length" select="@length"/>
                                                            </xsl:call-template>
                                                        </xsl:if -->
                                                    </div>
                                                </xsl:for-each>
                                            </section>
                                        </xsl:if>
                                    </form>
                                    </article>
                                    <!-- entry id -->
                                    <!-- TODO add ID for Microformat u-uid -->
                                    <xsl:if test="not(atom:id)">
                                        <div class="warning atom1 id">No entry ID</div>
                                    </xsl:if>
                                </xsl:for-each>
                            </xsl:when>
                            <xsl:otherwise>
                                <article class="entry">
                                  <h3 class="title">
                                    <a href="javascript:alert('Check source reStructuredText files.')">
                                      <xsl:text>No content</xsl:text>
                                    </a>
                                  </h3>
                                  <h4>This feed is empty</h4>
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
