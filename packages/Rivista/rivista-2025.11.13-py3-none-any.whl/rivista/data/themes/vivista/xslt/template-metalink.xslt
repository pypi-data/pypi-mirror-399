<?xml version="1.0" encoding="UTF-8" ?>
<!-- Copyright (C) 2025 Schimon Jehuda. Released under MIT license. -->
<xsl:stylesheet version="1.0" 
                xmlns:atom="http://www.w3.org/2005/Atom"
                xmlns:metalink4="urn:ietf:params:xml:ns:metalink"
                xmlns:xlink="http://www.w3.org/1999/xlink"
                xmlns:xml="http://www.w3.org/XML/1998/namespace"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/metalink4:metalink">
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
                    <xsl:with-param name="content" select="//atom:subtitle"/>
                </xsl:call-template>
                <xsl:call-template name="element-meta">
                    <xsl:with-param name="name" select="'generator'"/>
                    <xsl:with-param name="content" select="//atom:generator"/>
                </xsl:call-template>
                <xsl:call-template name="element-meta">
                    <xsl:with-param name="name" select="'mimetype'"/>
                    <xsl:with-param name="content" select="'application/xhtml+xml'"/>
                </xsl:call-template>
                <title>Metalink</title>
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
                        <h1 class="title">Metalink</h1>
                        <!-- Subtitle -->
                        <h2 class="subtitle">Metalink Download Description Format</h2>
                        <p>
                            <xsl:if test="string-length(metalink4:origin) &gt; 0">
                                <div class="author p-author">
                                    <xsl:value-of select="metalink4:origin"></xsl:value-of>
                                </div>
                            </xsl:if>
                            <xsl:if test="string-length(metalink4:published) &gt; 0">
                                <div class="published dt-published">
                                    <xsl:value-of select="metalink4:published"></xsl:value-of>
                                </div>
                            </xsl:if>
                            <xsl:if test="string-length(metalink4:updated) &gt; 0">
                                <div>
                                    <xsl:text>Updated: </xsl:text>
                                    <span class="updated dt-updated">
                                        <xsl:value-of select="metalink4:updated"></xsl:value-of>
                                    </span>
                                </div>
                            </xsl:if>
                            <xsl:if test="string-length(metalink4:dynamic) &gt; 0">
                                <div>
                                    <xsl:text>dynamic</xsl:text>
                                    <xsl:value-of select="metalink4:dynamic"></xsl:value-of>
                                </div>
                            </xsl:if>
                        </p>
                    </header>
                    <xsl:if test="count(metalink4:file) &gt; 1">
                        <section id="menu">
                            <details>
                            <summary>Files</summary>
                                <ol>
                                    <xsl:for-each select="metalink4:file">
                                        <li>
                                            <xsl:element name="a">
                                                <xsl:attribute name="href">
                                                    <xsl:text>#metalink-</xsl:text>
                                                    <xsl:value-of select="position()"/>
                                                </xsl:attribute>
                                                <xsl:value-of select="metalink4:identity"/>
                                          </xsl:element>
                                        </li>
                                    </xsl:for-each>
                                </ol>
                            </details>
                        </section>
                    </xsl:if>
                    <section id="articles">
                        <!-- Metalink -->
                        <xsl:choose>
                            <xsl:when test="metalink4:file">
                                <xsl:for-each select="metalink4:file">
                                    <article class="entry h-entry">
                                        <xsl:attribute name="id">
                                              <xsl:text>metalink-</xsl:text>
                                              <xsl:value-of select="position()"/>
                                        </xsl:attribute>
                                        <xsl:attribute name="lang">
                                            <xsl:value-of select="metalink4:language"/>
                                        </xsl:attribute>
                                        <!-- File title -->
                                        <h3 class="title p-name">
                                            <xsl:element name="span">
                                                <xsl:attribute name="id">
                                                    <xsl:text>metalink-</xsl:text>
                                                    <xsl:value-of select="position()"/>
                                                </xsl:attribute>
                                                <xsl:value-of select="metalink4:identity"/>
                                            </xsl:element>
                                        </h3>
                                        <!-- File properties -->
                                        <dl>
                                            <dt>Description</dt>
                                            <dd><xsl:value-of select="metalink4:description"/></dd>
                                            <dt>Filename</dt>
                                            <dd>
                                                <code>
                                                    <xsl:value-of select="@name"/>
                                                </code>
                                            </dd>
                                            <dt>Filesize</dt>
                                            <dd>
                                                <code>
                                                    <xsl:call-template name="transform-filesize">
                                                        <xsl:with-param name="length" select="metalink4:size"/>
                                                    </xsl:call-template>
                                                </code>
                                            </dd>
                                            <xsl:if test="string-length(metalink4:version) &gt; 0">
                                            <dt>Version</dt>
                                            <dd><xsl:value-of select="metalink4:version"/></dd>
                                            </xsl:if>
                                            <dt>References</dt>
                                            <table>
                                                <tbody>
                                                    <xsl:for-each select="metalink4:url">
                                                        <tr>
                                                            <th>URI</th>
                                                            <td>
                                                                <pre>
                                                                    <xsl:value-of select="text()"/>
                                                                </pre>
                                                            </td>
                                                        </tr>
                                                        <tr>
                                                            <th>Location</th>
                                                            <td><xsl:value-of select="@location"/></td>
                                                        </tr>
                                                        <tr>
                                                            <th>Priority</th>
                                                            <td><xsl:value-of select="@priority"/></td>
                                                        </tr>
                                                    </xsl:for-each>
                                                </tbody>
                                            </table>
                                        </dl>
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
                    <xsl:text>This is a Metalink Download Description </xsl:text>
                    <xsl:text>(MDD) document which was transformed </xsl:text>
                    <xsl:text>to HTML with an XSLT stylesheet; </xsl:text>
                    <xsl:text>the files thereof can be downloaded </xsl:text>
                    <xsl:text>with software that support The Metalink </xsl:text>
                    <xsl:text>Download Description Format (RFC 5854).</xsl:text>
                </footer>
                <!-- Document generator -->
                <xsl:comment>
                    <xsl:text>Document generator</xsl:text>
                </xsl:comment>
                <footer id="generator">
                    <xsl:text>Generated by </xsl:text>
                    <xsl:value-of select="metalink4:generator"/>
                </footer>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
