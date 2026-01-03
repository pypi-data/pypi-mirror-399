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
                            <xsl:text>Contact</xsl:text>
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
                            <xsl:with-param name="routine-title" select="'Contact'"/>
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
                    <xsl:if test="atom:entry/atom:link[@rel='enclosure' and @title='Photograph']">
                        <section id="publisher-profile">
                            <xsl:if test="atom:entry/atom:link[@rel='enclosure' and @title='Photograph']">
                                <xsl:element name="img">
                                    <xsl:attribute name="id">
                                        <xsl:text>publisher-profile-img</xsl:text>
                                    </xsl:attribute>
                                    <xsl:attribute name="alt">
                                        <xsl:text>Profile image</xsl:text>
                                    </xsl:attribute>
                                    <xsl:attribute name="src">
                                        <xsl:value-of select="atom:entry/atom:link[@rel='enclosure' and @title='Photograph']/@href"/>
                                    </xsl:attribute>
                                </xsl:element>
                            </xsl:if>
                            <xsl:if test="atom:entry/atom:link[@rel='enclosure' and @title='QR Code']">
                                <xsl:element name="img">
                                    <xsl:attribute name="id">
                                        <xsl:text>publisher-profile-qr</xsl:text>
                                    </xsl:attribute>
                                    <xsl:attribute name="alt">
                                        <xsl:text>QR Code</xsl:text>
                                    </xsl:attribute>
                                    <xsl:attribute name="src">
                                        <xsl:value-of select="atom:entry/atom:link[@rel='enclosure' and @title='QR Code']/@href"/>
                                    </xsl:attribute>
                                </xsl:element>
                            </xsl:if>
                        </section>
                    </xsl:if>
                    <section id="articles">
                        <xsl:call-template name="element-article-concise">
                            <xsl:with-param name="atom" select="atom:entry"/>
                        </xsl:call-template>
                    </section>
                    <section id="contact">
                        <h3>Contact form</h3>
                        <form action="/message" method="post">
                            <dl>
                                <dt>
                                    <label for="address">Address:</label>
                                </dt>
                                <dd>
                                    <input id="address"
                                           name="address"
                                           placeholder="XMPP or Email address"
                                           type="email"/>
                                </dd>
                                <dt>
                                    <label for="subject">Subject:</label>
                                </dt>
                                <dd>
                                    <input id="subject"
                                           name="subject"
                                           placeholder="Subject of concern"
                                           type="text"/>
                                </dd>
                                <dt>
                                    <label for="message">Message:</label>
                                </dt>
                                <dd>
                                    <textarea id="message"
                                              maxlength="100"
                                              name="message"
                                              minlength="50"
                                              placeholder="Input your message (minimum of 50 characters)."
                                              required=""
                                              rows="10"/>
                                </dd>
                                <dt>
                                    <label for="enclosure">Attachment:</label>
                                </dt>
                                <dd>
                                    <input id="enclosure"
                                           name="enclosure"
                                           type="file"/>
                                </dd>
                            </dl>
                            <hr/>
                            <button type="submit">Proceed</button>
                        </form>
                    </section>
                </div>
                <xsl:call-template name="element-navigation-bar">
                    <xsl:with-param name="relation" select="'navigation-bottom'"/>
                    <xsl:with-param name="element" select="atom:link[@rel='navigation-bottom']"/>
                </xsl:call-template>
                <!-- Document generator -->
                <xsl:call-template name="element-generator">
                    <xsl:with-param name="generator" select="atom:generator"/>
                </xsl:call-template>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
