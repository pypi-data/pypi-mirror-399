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
                            <xsl:text>Comments: </xsl:text>
                            <xsl:value-of select="atom:title"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:text>Comments</xsl:text>
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
                <xsl:call-template name="elements-link-relation">
                    <xsl:with-param name="links-relation" select="atom:link[@rel='icon']"/>
                    <xsl:with-param name="relation" select="'icon'"/>
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
                        <!-- page title -->
                        <h1 id="title">Comments</h1>
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
                    <xsl:if test="count(atom:entry) &gt; 1">
                        <section id="menu">
                           <h3>Recent comments</h3>
                           <!-- xsl:for-each select="atom:entry[position() &lt;21]" -->
                            <ol>
                                <xsl:for-each select="atom:entry[not(position() &gt; 20)]">
                                    <li>
                                        <xsl:element name="a">
                                            <xsl:attribute name="href">
                                                 <xsl:text>#rivista-</xsl:text>
                                                 <xsl:value-of select="position()"/>
                                            </xsl:attribute>
                                            <xsl:choose>
                                                <xsl:when test="string-length(atom:title) &gt; 0">
                                                    <xsl:value-of select="atom:title"/>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:text>*** No Title ***</xsl:text>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                      </xsl:element>
                                    </li>
                                </xsl:for-each>
                            </ol>
                        </section>
                    </xsl:if>
                    <section class="comment">
                        <form action="/comment" method="post">
                            <h3>Post a comment</h3>
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
                                    <label for="title">Title:</label>
                                </dt>
                                <dd>
                                    <input id="title"
                                            name="title"
                                            placeholder="Title"
                                            required=""
                                            type="text"/>
                                </dd>
                                <dt>
                                    <label for="comment">Comment:</label>
                                </dt>
                                <dd>
                                    <textarea id="comment"
                                              maxlength="100"
                                              name="comment"
                                              minlength="50"
                                              placeholder="Please input your comment (minimum of 50 characters)."
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
                                <button type="submit">Proceed</button>
                            </dl>
                        </form>
                    </section>
                    <section id="articles">
                        <!-- feed entry -->
                        <xsl:choose>
                            <xsl:when test="atom:entry">
                                <xsl:for-each select="atom:entry[not(position() &gt; 20)]">
                                    <article class="entry h-entry">
                                        <!-- entry title -->
                                        <h3 class="title p-name">
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
                                                <xsl:attribute name="id">
                                                    <xsl:text>rivista-</xsl:text>
                                                    <xsl:value-of select="position()"/>
                                                </xsl:attribute>
                                                <xsl:choose>
                                                    <xsl:when test="string-length(atom:title) &gt; 0">
                                                        <xsl:value-of select="atom:title"/>
                                                    </xsl:when>
                                                    <xsl:otherwise>
                                                        <xsl:text>*** No Title ***</xsl:text>
                                                    </xsl:otherwise>
                                                </xsl:choose>
                                            </xsl:element>
                                        </h3>
                                        <!-- geographic location -->
                                        <xsl:choose>
                                            <xsl:when test="geo:lat and geo:long">
                                                <xsl:variable name="lat" select="geo:lat"/>
                                                <xsl:variable name="lng" select="geo:long"/>
                                                <span class="geolocation p-location">
                                                    <a href="geo:{$lat},{$lng}">📍</a>
                                                </span>
                                            </xsl:when>
                                            <xsl:when test="geo:Point">
                                                <xsl:variable name="lat" select="geo:Point/geo:lat"/>
                                                <xsl:variable name="lng" select="geo:Point/geo:long"/>
                                                <span class="geolocation p-location">
                                                    <a href="geo:{$lat},{$lng}">📍</a>
                                                </span>
                                            </xsl:when>
                                        </xsl:choose>
                                        <!-- entry date -->
                                        <xsl:element name="h4">
                                            <xsl:choose>
                                                <xsl:when test="atom:updated">
                                                    <xsl:attribute name="class">
                                                        <xsl:text>updated dt-updated</xsl:text>
                                                    </xsl:attribute>
                                                    <xsl:value-of select="atom:updated"/>
                                                </xsl:when>
                                                <xsl:when test="atom:published">
                                                    <xsl:attribute name="class">
                                                        <xsl:text>published dt-published</xsl:text>
                                                    </xsl:attribute>
                                                    <xsl:value-of select="atom:published"/>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <h4 class="warning atom1 published"></h4>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </xsl:element>
                                        <!-- entry author -->
                                        <xsl:if test="atom:author">
                                            <h4 class="author h-card p-author">
                                                <xsl:text>By </xsl:text>
                                                <xsl:choose>
                                                    <xsl:when test="atom:author/atom:email">
                                                        <xsl:element name="a">
                                                            <xsl:attribute name="href">
                                                                <xsl:text>mailto:</xsl:text>
                                                                    <xsl:value-of select="atom:author/atom:email"/>
                                                            </xsl:attribute>
                                                            <xsl:attribute name="title">
                                                                <xsl:text>Send an Email to </xsl:text>
                                                                <xsl:value-of select="atom:author/atom:email"/>
                                                            </xsl:attribute>
                                                            <xsl:value-of select="atom:author/atom:name"/>
                                                        </xsl:element>
                                                    </xsl:when>
                                                    <xsl:when test="atom:author/atom:uri">
                                                        <xsl:element name="a">
                                                            <xsl:attribute name="href">
                                                                <xsl:value-of select="atom:author/atom:uri"/>
                                                            </xsl:attribute>
                                                            <xsl:attribute name="title">
                                                                <xsl:value-of select="atom:author/atom:summary"/>
                                                            </xsl:attribute>
                                                            <xsl:value-of select="atom:author/atom:name"/>
                                                        </xsl:element>
                                                    </xsl:when>
                                                    <xsl:when test="atom:author/atom:name">
                                                        <xsl:value-of select="atom:author/atom:name"/>
                                                    </xsl:when>
                                                    <xsl:when test="atom:uri">
                                                        <xsl:value-of select="atom:uri"/>
                                                    </xsl:when>
                                                </xsl:choose>
                                            </h4>
                                        </xsl:if>
                                        <h5 class="related">
                                            <xsl:if test="atom:link[@rel='alternate' and @type='x-scheme-handler/xmpp']">
                                                <xsl:element name="a">
                                                    <xsl:attribute name="href">
                                                        <xsl:value-of select="atom:link[@rel='alternate' and @type='x-scheme-handler/xmpp']/@href"/>
                                                    </xsl:attribute>
                                                    <xsl:attribute name="class">
                                                        <xsl:text>rivista-jabber</xsl:text>
                                                    </xsl:attribute>
                                                    <xsl:text>💡️ Source (XMPP)</xsl:text>
                                                </xsl:element>
                                            </xsl:if>
                                            <xsl:if test="atom:link[@rel='contact']">
                                                <xsl:element name="a">
                                                    <xsl:attribute name="href">
                                                        <xsl:value-of select="atom:link[@rel='contact']/@href"/>
                                                    </xsl:attribute>
                                                    <xsl:attribute name="class">
                                                        <xsl:text>contact-uri</xsl:text>
                                                    </xsl:attribute>
                                                    <xsl:text>🪪️ Contact</xsl:text>
                                                </xsl:element>
                                            </xsl:if>
                                            <xsl:if test="atom:link[@rel='replies']">
                                                <xsl:element name="a">
                                                    <xsl:attribute name="href">
                                                        <xsl:value-of select="atom:link[@rel='replies']/@href"/>
                                                    </xsl:attribute>
                                                    <xsl:attribute name="class">
                                                        <xsl:text>rivista-replies</xsl:text>
                                                    </xsl:attribute>
                                                    <xsl:text>💬 Discussion (XMPP)</xsl:text>
                                                </xsl:element>
                                            </xsl:if>
                                            <xsl:if test="atom:link[@rel='alternate' and contains(@type,'html')]">
                                                <xsl:element name="a">
                                                    <xsl:attribute name="href">
                                                        <xsl:value-of select="atom:link[@rel='alternate' and contains(@type,'html')]/@href"/>
                                                    </xsl:attribute>
                                                    <xsl:text>📜 HTML (Version)</xsl:text>
                                                </xsl:element>
                                            </xsl:if>
                                            <xsl:if test="atom:link[@rel='related' and contains(@type,'html')]">
                                                <xsl:element name="a">
                                                    <xsl:attribute name="href">
                                                        <xsl:value-of select="atom:link[@rel='related' and contains(@type,'html')]/@href"/>
                                                    </xsl:attribute>
                                                    <xsl:text>📜 HTML (Related)</xsl:text>
                                                </xsl:element>
                                            </xsl:if>
                                        </h5>
                                        <!-- entry summary -->
                                        <xsl:if test="string-length(atom:summary) &gt; 0">
                                            <h4>Summary</h4>
                                            <section class="summary p-summary">
                                                <xsl:choose>
                                                    <xsl:when test="atom:summary[contains(@type,'html')]">
                                                        <xsl:attribute name="type">
                                                            <xsl:value-of select="atom:summary/@type"/>
                                                        </xsl:attribute>
                                                        <xsl:value-of select="atom:summary" disable-output-escaping="yes"/>
                                                    </xsl:when>
                                                    <xsl:when test="atom:summary[contains(@type,'text')]">
                                                        <xsl:attribute name="type">
                                                            <xsl:value-of select="atom:summary/@type"/>
                                                        </xsl:attribute>
                                                        <xsl:value-of select="atom:summary"/>
                                                    </xsl:when>
                                                    <xsl:when test="atom:summary[contains(@type,'base64')]">
                                                        <!-- TODO add xsl:template to handle inline media -->
                                                    </xsl:when>
                                                    <xsl:otherwise>
                                                        <xsl:value-of select="atom:summary" disable-output-escaping="yes"/>
                                                    </xsl:otherwise>
                                                </xsl:choose>
                                            </section>
                                        </xsl:if>
                                        <!-- entry content -->
                                        <xsl:if test="string-length(atom:content) &gt; 0">
                                            <h4>Content</h4>
                                            <section class="content e-content">
                                                <xsl:choose>
                                                    <xsl:when test="atom:content[contains(@type,'html')]">
                                                        <xsl:attribute name="type">
                                                            <xsl:value-of select="atom:content/@type"/>
                                                        </xsl:attribute>
                                                        <xsl:value-of select="atom:content" disable-output-escaping="yes"/>
                                                    </xsl:when>
                                                    <xsl:when test="atom:content[contains(@type,'text')]">
                                                        <xsl:attribute name="type">
                                                            <xsl:value-of select="atom:content/@type"/>
                                                        </xsl:attribute>
                                                        <xsl:value-of select="atom:content"/>
                                                    </xsl:when>
                                                    <xsl:when test="atom:content[contains(@type,'base64')]">
                                                        <!-- TODO add xsl:template to handle inline media -->
                                                    </xsl:when>
                                                    <xsl:otherwise>
                                                        <xsl:value-of select="atom:content" disable-output-escaping="yes"/>
                                                    </xsl:otherwise>
                                                </xsl:choose>
                                            </section>
                                        </xsl:if>
                                        <!-- entry tags -->
                                        <xsl:if test="atom:category">
                                            <h4>Tags</h4>
                                            <section class="tags">
                                                <xsl:for-each select="atom:category">
                                                    <xsl:element name="span">
                                                        <xsl:attribute name="p-category">
                                                            <xsl:value-of select="@term"/>
                                                        </xsl:attribute>
                                                        <xsl:value-of select="@term"/>
                                                    </xsl:element>
                                                </xsl:for-each>
                                            </section>
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
                                                            <xsl:call-template name="extract-filename">
                                                                <xsl:with-param name="url" select="@href"/>
                                                            </xsl:call-template>
                                                        </xsl:element>
                                                        <xsl:if test="@length &gt; 0">
                                                            <xsl:call-template name="transform-filesize">
                                                                <xsl:with-param name="length" select="@length"/>
                                                            </xsl:call-template>
                                                        </xsl:if>
                                                    </div>
                                                </xsl:for-each>
                                            </section>
                                        </xsl:if>
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
                                  <h3>No comments, yet.</h3>
                                  <h4>This comments feed is currently empty.</h4>
                                  <section class="content">
                                    <xsl:text>There are no comments </xsl:text>
                                    <xsl:text>for this article.</xsl:text>
                                    <br/>
                                    <xsl:text>Be the first to comment.</xsl:text>
                                  </section>
                                </article>
                            </xsl:otherwise>
                        </xsl:choose>
                    </section>
                </div>
                <xsl:call-template name="element-navigation">
                    <xsl:with-param name="entry-count" select="count(atom:entry)"/>
                    <xsl:with-param name="previous" select="atom:link[@rel='prev']"/>
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
                <!-- Document generator -->
                <xsl:call-template name="element-generator">
                    <xsl:with-param name="generator" select="atom:generator"/>
                </xsl:call-template>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
